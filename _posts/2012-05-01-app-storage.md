---
layout: post
title: Application Persistence and Data Storage
--- 


The majority of applications need to store information between sessions such as user preferences, GUI state and app state (connections, last used paths, etc.). This scenario is usually the easiest to handle: writing/reading an *.ini or *.xml file is usually sufficient as long as we pay attention to: 

 - *Backward compatibility*: We must make sure that new field/data can be added without breaking the original format.
 - *Forward compatibility*: Can old version of the app safely ignore new fields AND retain their values on save ?
 - *Robust commit to disk*: We need to make sure we cannot corrupt our setting file if serialization fails: Usually, we would rename the original file (myfile.xml->myfile.bkp), save the new setting file (tmp.xml) then on success, rename it (myfile.xml). If anything bad append during serialization or filesystem access we can recover the original file (myfile.bkp) 

Editing apps dealing very large datasets (several hundred Gigabytes) are a lot more challenging. Users typically visualize and edit the raw data to generate a "processed output". As the user is free to change the processing "recipe" at anytime, all changes must be reversible, but the size of the data makes it  impossible to keep all processed data in system memory. 
Ideally, we'd like to avoid the issue altogether by not storing any processed info but create it on the fly from the rawdata everytime. This is possible in special cases were processing is fast and a small amount of raw data is fetched from disk. In the general case, we need to deal with keeping our cache of processed data in sync with the processing settings so we don't corrupt our projet on app crash or power failure.  

Real-time acquisition and visualization are more challenging since raw data, processed data cache (visualization) and the editing settings (used to process the raw data for visualization) most be kept coherent. Project data size may be in the order of several hundred gigabyte, so processed info/cache will not fit in system memory. It is important to design the storage/persistence system so that projects cannot be corrupt by a crash or power failure. 

### SQL Backend ###
DBMS -with transaction support, extensible schema and plenty of tools- may be a good way to implement a robust, forward/backward compatible persistence layer. 
To keep application deployment simple, an in-process SQL DB is usually best. The excellent [SQLite](http://www.sqlite.org/) usually come to mind and we have used it successfully in several projects, but there a few things to consider when using SQL as the backend for object-oriented apps:

- Cost of the [Object-relational impedance mismatch](http://en.wikipedia.org/wiki/Object-relational_impedance_mismatch). Using or writing a [Object Relational Mapping](http://en.wikipedia.org/wiki/Object-relational_mapping) may help... or not. On many occasions, I felt like I had to write quite a bit of code to achieve something that is inherently simple. I've tried many different approaches and libs, but I cannot say I have found a concise solution I really like.     
- Do you really need the power (and cost) of SQL?. What queries do you need? is a key/value store good enough?
- Performance: Is the DB fast enough for your usage pattern ?

###Data Store###
When project data grows to several hundred GB, DBMS performances becomes sub-optimal when read/writing large binary-blob at high frequency. In this particular case, we could do without SQL language and use a data-store with indexing. 

####Cache System and Paged I/O####
To implement our own data store we need to turn off OS caching and buffering so we control memory usage. This means that I/O must be disk-sector aligned and at least 1 sector in size. For hard drive, sector size is usually 512 or 4096 bytes. 
The diagram below shows the structure of the storage system: 

![storage engine](/assets/images/storage-engine.png)

The cache is page-based and may be shared across multiple stores (i.e files) with same page size. In an heavily multi-threaded scenario, cache contention could be an issue, but in our case, shared Least-Recently-Used (LRU) schemes between store provides significant memory savings. In general, we do not mix index stores and data stores on the same cache even if the have the same page-size, but we are free to assign a dedicated cache to a specific store, if needed.

####Transactions and Write-Ahead-Logging (WAL) ####
We would like to implement transaction in our storage system to guarantee data-store integrity and support rollback. 
At the store (i.e. file) level, we only have the concept of *pages* ( fixed size and varying size *records* abstractions are built on top of pages). All store access comes from cache system, the client code doesn't access this level. We implement a page-based write-ahead-log as a separate file: 

 - *Append*: new pages is appended to the store file.
 - *Read*: Fetch page from the store file unless the page was written during the current transaction, in which case we fetch it from the WAL file 
 - *Write*: if first write for the transaction, create a page in WAL file, otherwise overwrite the existing WAL page. The store is not changed.
 - *commit*: WAL pages are written to store file and WAL is cleared. The store file starts with as a header (first sector) where status info are kept. If commit cannot complete (crash, loss of power), the commit will be resume on restart. 
 - *rollback*: truncate the store file back to last commit size (i.e. discard new pages), and clear the WAL (i.e. discard write changes)
 - *Delete*: deleted pages are written to a separate journal. In our case, data is rarely deleted, so we only implemented offline "compacting" to reclaim disk-space. 

At the Storage system level, we kept a simple journal of commits. If some stores could not commit before a failure, we notify them to commit their WAL on restart.

####Thread-Safety####
Several worker threads (data logger, processing filters, Main GUI, etc.) may access the storage system concurrently so we have to make sure our system is thread-safe. Each cache implement a multiple readers/single writer serialization while each store access is serialized per store instance. High level operations (adding store, transaction commit/rollback, etc.) are serial and need to acquire a global lock.
