--- 
layout: post
title: "Automating Point cloud Cleaning with Connected Component Analysis"
---

Beam scanning sensors (i.e. lidar, multibeam/interferometric sonars) generate a LOT of point data (gigabytes per survey hour) so cleaning out noisy points quickly becomes a challenge. Sometimes the basic tools can do 99% of the job: running an amplitude filter and then a median filter on some dataset would clean most of the bad points.

![](/assets/images/arizona-cropped.png)


but sometime it won't:
![](/assets/images/noisy-mb.jpg)


Sure, we can always resort to manual cleaning tools (polygon crop, etc.) but looking at point cloud data carefully we sometimes feels that  more automation should be possible. Intuitively, large clusters of noisy points survive the 2d-median filter (since they are statistically significant) but should be eliminated. 

### Connected component ###

This is where the connected component could help. If we define a connected component as the path connecting points where the elevation between two points are less that a minimum height we define.   
Let's tag all points by connected components and see if this would help our cleaning process:

<table>
<tr><td><img src="/assets/images/boat-colors.jpg"/></td>
<td><img src="/assets/images/boat-2-comp.png" /></td></tr>
</table>

We see that we have 2 distinct components on the image on the right: 1) the seafloor green, 2) deck of the shipwreck (red). In this special case, the 2 principals components are or interest and noise is absent, so let's see a what happen with a noisier interferometric sonar dataset:

![](/assets/images/noisy-cloud.png)

Cleary, the first component contains most of seafloor (green) while the biggest artifacts (surface reflection, schools of fish, etc.) are separated into their own component (magenta, yellow, cyan). All smaller components (noise) are shown in grey.


###Implementation ###

Connected component are expensive to compute as they require to sort the entire dataset and triangulate it in 2D. Out-of-core Delaunay triangulation is usually very slow, but Martin Isenburg and al. (see ref) describe an excellent streaming approach which works very well for large remote sensing datasets.  


####Z-Threshold####
We need to specify a z separation threshold to test for inclusion in a connected component. This values is critical as it will determine how many components will we get. In practice, there is often sensible ways to define it based on the sensor resolution, survey condition or processing requirement.    


###Conclusion###
Compare to more conventional cleaning tools, connected components are able to move away from a local statistical analysis and use adjacency properties of the point cloud to classify point clusters. This more powerful analysis comes with a run-time cost (processing time and memory usage) but can help clean challenging dataset in a few clicks.   


### References ###

[Real-time extraction of connected components in 3-D sonar range images; Auran, P.G. ; Dept. of Eng. Cybernetics, Norwegian Univ. of Sci. & Technol., Trondheim, Norway]( http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=517131 )

[Streaming Computation of Delaunay Triangulations; Martin Isenburg, Yuanxin (Leo) Liu, Jonathan Shewchuk,     Jack Snoeyink](http://www.cs.unc.edu/~isenburg/sd/)



 