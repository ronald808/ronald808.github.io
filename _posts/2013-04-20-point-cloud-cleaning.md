--- 
layout: post
title: "Automating Point Cloud Cleaning with Connected Component Analysis"
---

Several types of remote sensors generate point cloud data. Scanning systems such as [LiDAR](http://en.wikipedia.org/wiki/Lidar) are used extensively on land, while multibeam echosounders have been used for decades to map the oceans. These technologies differ but the trend is the same: resolution is increasing, and datasets are getting bigger and take longer to process. Cleaning hundred of gigabytes of data efficiently becomes a challenge if it requires too much manual editing. Sometimes simple tools can do 99% of the job: running an amplitude filter and then a median filter on some multibeam dataset would clean most of the bad points:

![](/assets/images/arizona-cropped.png)


but some dataset can be more challenging...
<img src="/assets/images/noisy-mb.jpg" style="width:400px"/>


Looking at some raw point cloud data, we sometimes wish that more automation was possible. For instance, large clusters of noisy points often survive a 2D-median filter since they are statistically significant within the filter radius. 

### Connected component ###

This is where connected component analysis can help. In the case above, we define a connected component as a path connecting points, such that the elevation between two consecutive points along the path is less than a user-defined threshold. Points are then tagged by their connected components, and we can separate the components we wish to keep (terrain, building, seafloor, ...) from the ones representing noise or artifact in the data (tree canopy, boat wake, school of fish,...)

The multibeam data below illustrates the process:

<img src="/assets/images/boat-colors.jpg" style="width:390px;padding:0;padding-bottom:10px;"/>
<img src="/assets/images/boat-connect-comp.png" style="height:400px;padding:0;"/>

<table>
<tr><td>
<td></td></tr>

</table>

We see that we have 2 distinct components on the image on the right: 1) the seafloor (green), 2) the deck of the shipwreck (red). In this special case, the 2 principal components of interest stand out and the noise as been rejected into smaller components. 

Let's see a what happens with a noisier interferometric sonar dataset:

![](/assets/images/noisy-cloud.png)

Clearly, the first component contains most of the seafloor (green), while the biggest artifacts (surface reflection, schools of fish, etc.) are separated into their own components (magenta, yellow, cyan). All smaller components (noise) are shown in gray. In this case, user intervention to clean the dataset is limited to selecting the first component and rejecting all others.

###Implementation ###

Connected component are expensive to compute, as they require sorting the entire dataset and triangulating it in 2D. Out-of-core Delaunay triangulation is very slow, but Martin Isenburg and al. (*see refs below*) describes an excellent streaming approach which works very well for large remote sensing datasets.


####Z-Threshold####
We need to specify a z separation threshold to test for inclusion in a connected component. This value is important, as it will determine how many components we will get. Although there are many ways to pick this threshold, in practice, considering the sensor resolution and noise envelope works well.


###Conclusion###
Compared to more conventional cleaning tools, connected components go beyond local statistical analysis and use point adjacency to classify the point cloud. Of course, this global analysis comes with a run-time cost (processing time and memory usage) but it can help clean challenging datasets in a few clicks. The analysis leans itself well to a streaming implementation, but parallelizing the algorithm is challenging.

### References ###

[Real-time extraction of connected components in 3-D sonar range images; Auran, P.G. ; Dept. of Eng. Cybernetics, Norwegian Univ. of Sci. & Technol., Trondheim, Norway]( http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=517131 )

[Streaming Computation of Delaunay Triangulations; Martin Isenburg, Yuanxin (Leo) Liu, Jonathan Shewchuk,     Jack Snoeyink](http://www.cs.unc.edu/~isenburg/sd/)



 