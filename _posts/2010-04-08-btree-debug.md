---
title: "Debugging B+Tree"
layout: post
---

B+Trees are search trees optimized for block-oriented storages such as hard drives. They are used extensively in databases and file systems and we recently use them as indexing structure for our [storage engine]({% post_url 2011-05-01-app-storage %} ).

Unlike their in-memory cousins (red-black tree, binary search tree, etc.) B+Tree container are harder to find (no STL/Boost). The reason may be that B+Tree are not "free standing" algorithms as they need an I/O interface. Implementation details may also have an impact on performance so implementer may be tempted to start from scratch. 

Fortunately, good readings on B+Tree insert/find/erase/iterate operations are available online.

- [http://web.cse.ohio-state.edu/~gurari/course/cis680/cis680Ch13.html](http://web.cse.ohio-state.edu/~gurari/course/cis680/cis680Ch13.html)
- [http://en.wikipedia.org/wiki/B%2B_tree](http://en.wikipedia.org/wiki/B%2B_tree)
- [http://www.cs.usfca.edu/~galles/visualization/BPlusTree.html](http://www.cs.usfca.edu/~galles/visualization/BPlusTree.html)


Implementation is not overly complex, but its easy to make mistakes especially in the "erase" function. 

Testing is pretty easy though: We used another {key,value} container to test our implementation: we run randomly generated batches of insert/delete/find operations and cross-check our B+Tree against a <code>std::map</code>

Once a bug is found, figuring out what when wrong could be a bit tedious as the erroneous tree re-arrangement may have occurred many operations before.  To narrow it down, we run a invariant check on the tree after each operation so we catch problems early.

Even then, staring at the code may not help much unless we can print the tree somehow. I have found [Graphviz](http://www.graphviz.org/) convenient for this task: we traverse our tree (using a visitor pattern) and write each node in **dot** format  into a file.
To connect the graph, we use the key/value of each node in the naming pattern of **dot** nodes.

Finally, we generate the * *.svg* output using the commande line:

		C:\tools\Graphviz\bin\dot.exe -Tsvg c:\temp\btree.dot -o c:\temp\btree.svg"

The graphs:

![B tree svg]({{site.baseurl}}/assets/images/btree-sample.png)

If we print the tree before a after the erroneous operation, we can usually visualize what when wrong and trace the issue back the code.
 


  





 


 





   