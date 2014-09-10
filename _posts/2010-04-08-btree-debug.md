---
title: "Debugging B+Tree"
layout: post
---

B+Trees are {Key, Value} indexes optimized for efficient retrieval in a block-orientated storage context (i.e. disk). They are used extensively in databases/filesystems as the go-to algorithm for out-of-core indexing. In our case, we often implement our own storage system for raw data acquisition and processing so B+Tree are perfect for the task.

Unlike its in-memory cousins (Red-black tree, binary search tree, etc.) ready to use B+Tree container are hard to find (no STL/Boost implementation). The reason may be  that B+Tree are not free standing algorithms as you need to define an I/O interface and some implementation details may have to be tailored to your application.

Fortunately, good readings on B+Tree insert/find/erase/iterate operations are available online.

- [http://web.cse.ohio-state.edu/~gurari/course/cis680/cis680Ch13.html](http://web.cse.ohio-state.edu/~gurari/course/cis680/cis680Ch13.html)
- [http://en.wikipedia.org/wiki/B%2B_tree](http://en.wikipedia.org/wiki/B%2B_tree)
- [http://www.cs.usfca.edu/~galles/visualization/BPlusTree.html](http://www.cs.usfca.edu/~galles/visualization/BPlusTree.html)


Implementation is not overly complex, but its easy to make mistakes especially in "erase" operation. 

Testing is pretty easy though, as you can use another {key,value} container to test out implementation: we run randomly generated batches of insert/delete/find operation and cross-check our B+Tree against a <code>std::map</code>

Once a bug is found, figuring out what when wrong could be a bit tedious as the erroneous tree re-arrangements may have occurred many operations before.  To narrow it down, we run a invariant check on the tree after each operation so we catch problem early.

Even then, staring at the code may not help much unless we can print the tree somehow. I have found that [Graphviz](http://www.graphviz.org/) is both easy en convenient for this task: we traverse our tree (using a visitor pattern) and write each node in **dot** format  into a file
To connect the graph, we use the key/value of each node in the naming pattern of **dot** nodes.

We generate the * *.svg* output using the commande line:

		C:\tools\Graphviz\bin\dot.exe -Tsvg c:\temp\btree.dot -o c:\temp\btree.svg"

The graphs:

![B tree svg](img/btree-sample.png)




  





 


 





   