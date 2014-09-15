--- 
layout: post
title: "Automating Point cloud Cleaning with Connected Component Analysis"
---

Several types of remote sensors generates point cloud data. Scanning systems such as [LiDAR](http://en.wikipedia.org/wiki/Lidar) are used extensively on land while multibeam echosounder have been used for decades to map the Earth's oceans. The technology differs but the trend is the same: the number and resolution of surveys are increasing;  datasets are getting bigger and take longer to process. Cleaning hundred of Gigabytes of data efficiently becomes a challenge if it requires to much manual work. Sometimes simple tools can do 99% of the job: running an amplitude filter and then a median filter on some multibeam dataset would clean most of the bad points.

![](/assets/images/arizona-cropped.png)


but some dataset can be more challenging...
![](/assets/images/noisy-mb.jpg)


Looking at raw point cloud data we sometimes feels that  more automation should be possible. For instance, large clusters of noisy points often survive a 2D-median filter since they are statistically significant within the filter radius. 

### Connected component ###

This is where connected component analysis could help. In this case, we would define a connected component as a path connecting points such that the elevation between two consecutive point along the path is less than a user-defined threshold. Points could then be tagged by their connected components so we can decide which components to keep (terrain, building, seafloor, ...) and which ones represents noise or artifact in the data ( canopy, boat wake, school of fish,...)

The multibeam data below illustrates the process:

<table>
<tr><td><img src="/assets/images/boat-colors.jpg"/></td>
<td><img src="/assets/images/boat-2-comp.png" /></td></tr>
</table>

We see that we have 2 distinct components on the image on the right: 1) the seafloor green, 2) deck of the shipwreck (red). In this special case, the 2 principals components of interest stands out and the noise as been rejected in smaller component. 

Let's see a what happen with a noisier interferometric sonar dataset:

![](/assets/images/noisy-cloud.png)

Cleary, the first component contains most of seafloor (green) while the biggest artifacts (surface reflection, schools of fish, etc.) are separated into their own component (magenta, yellow, cyan). All smaller components (noise) are shown in grey. In this case, user intervention to clean the dataset is limited to selecting the first component and rejecting all others.

###Implementation ###

Connected component are expensive to compute as they require to sort the entire dataset and triangulate it in 2D. Out-of-core Delaunay triangulation is usually very slow, but Martin Isenburg and al. (*see refs below*) describe an excellent streaming approach which works very well for large remote sensing datasets.  


####Z-Threshold####
We need to specify a z separation threshold to test for inclusion in a connected component. This values is critical as it will determine how many components will we get. In practice, there is often sensible ways to define it based on the sensor resolution, survey condition or processing requirement.    


###Conclusion###
Compare to more conventional cleaning tools, connected components go beyond local statistical analysis to look at point adjacency in order to classify points. Of course, this global analysis comes with a run-time cost (processing time and memory usage) but can help clean challenging dataset in a few clicks. The analysis lean itself well to a streaming implementation, but paralleling the algorithm is challenging.

### References ###

[Real-time extraction of connected components in 3-D sonar range images; Auran, P.G. ; Dept. of Eng. Cybernetics, Norwegian Univ. of Sci. & Technol., Trondheim, Norway]( http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=517131 )

[Streaming Computation of Delaunay Triangulations; Martin Isenburg, Yuanxin (Leo) Liu, Jonathan Shewchuk,     Jack Snoeyink](http://www.cs.unc.edu/~isenburg/sd/)



 