---
layout: post
title: Application Persistence and Data Storage
--- 

###Settings Persistence###
 
The majority of applications need to store information between sessions, such as user preferences, GUI state and app state (connections, last used paths, etc.). A simple way to do this is by writing/reading an *.ini or *.xml file. It is often sufficient, as long as we pay attention to: 

 - *Backward compatibility*: Can new field/data be added without breaking the original format?
 - *Forward compatibility*: Can old versions of the app safely ignore new fields AND retain their value on save?
 - *Robust commit to disk*: We need to make sure we cannot corrupt our setting file if serialization fails: Usually, we would rename the original file (myfile.xml->myfile.bkp), save the new setting file ({tmppath}.xml) then on success, rename it (myfile.xml). If anything fails during serialization/filesystem access, we can recover the original file (myfile.bkp).

###App Projects###

For applications handling/editing large datasets (several hundred gigabytes), persistence is more challenging. These applications usually introduce the concept of *projects* to organize raw data input, processing settings and output files. While working on such applications, I strive to keep the application as interactive as possible with WYSIWYG editing, which usually requires a fair amount of synchronization between disk and system memory. The store system must be designed carefully to prevent project corruption on application crash or loss of power. 

#### SQL Backend ####
DBMS -with transaction support, extensible schemas and plenty of tools- can be a good solution for such projects. 
In-process SQL helps in keeping application deployment simple, so I chose the excellent [SQLite](http://www.sqlite.org/) as a backend for several editing apps. Using an SQL backend in object-oriented apps comes with a few caveats though:

- Cost of the [Object-relational impedance mismatch](http://en.wikipedia.org/wiki/Object-relational_impedance_mismatch). Using or writing an [Object Relational Mapping](http://en.wikipedia.org/wiki/Object-relational_mapping) may help... or not. On many occasions, I felt like I had to write quite a bit of code to achieve something that was inherently simple. I have tried many different approaches and libs over the years, but I cannot say that I have found a concise solution I really like.     
- Do you really need the power (and cost) of SQL?. What queries do you need? is a key/value store good enough?
- Performance: Is the DB fast enough for your usage pattern?

####Data Store####

When project data grows to several hundred GB, DBMS performance may become sub-optimal when read/writing large binary-blob at frequently. On some projects, I had to do without SQL language support and use a data-store with indexing instead. 

#####Cache System and Paged I/O#####

To implement our own data store we need to turn off OS caching and buffering so we control memory usage. On Windows, this means that I/O must be disk-sector aligned and at least 1 sector in size. For hard drives, sector size is usually 512 or 4096 bytes. 
The diagram below shows the structure of the storage system: 

![storage engine](/assets/images/storage-engine.png)

Each cache is page-based and may be shared across multiple stores (i.e files) with same page size. In an heavily multi-threaded scenario, cache contention could be an issue, but in our case, shared Least-Recently-Used (LRU) schemes between stores provides significant memory savings. In general, we do not mix index stores and data stores on the same cache even if they have the same page-size. A caching system is pretty flexible as we can define a quota per cache and assign a dedicated cache to a specific store, if needed.

#####Transactions and Write-Ahead-Logging (WAL) #####

In order to guarantee data-store integrity and to support rollback, we can add the concept of transactions to our storage system. At the store (i.e. file) level, we only have the concept of *pages* (fixed size and varying size *records* abstractions are built on top of pages). The store is accessed through the cache system, and the client code cannot access it directly. This design simplifies thread-safety and encapsulation of responsibilities. We implement a page-based write-ahead-log as a separate file: 

 - *Append*: new pages are added at the end of the store file.
 - *Read*: fetch page from the store file unless the page was written during the current transaction, in which case we fetch it from the WAL file 
 - *Write*: if first write for the transaction, create a page in WAL file, otherwise overwrite the existing WAL page. The store is not changed.
 - *commit*: WAL pages are written to store file and WAL is cleared. The store file starts with a header (first sector) where status info is kept. If the commit cannot complete (crash, loss of power), the commit will resume on restart. 
 - *rollback*: truncate the store file back to last the commit size (i.e. discard new pages), and clear the WAL (i.e. discard write changes)
 - *Delete*: deleted pages are written to a separate journal. In our case, data is rarely deleted, so we only implemented offline "compacting" to reclaim disk-space. 

At the Storage system level, we kept a simple journal of commits. If some stores could not commit before a failure, we notify them to commit their WAL on restart.

#####Thread-Safety#####

Several worker threads (data logger, processing filters, Main GUI, etc.) may access the storage system concurrently so we have to make sure our system is thread-safe. Each cache implements a multiple readers/single writer serialization, and each store access is serialized on a per store basis. Infrequent high level operations such as adding stores, transaction commit/rollback are serialized and need to acquire a global lock.
