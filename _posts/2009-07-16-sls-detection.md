---
layout: post
title: Objects Detection in  Sonar Images
---

Side-looking sonars transmit acoustic pulses and record the back-scattered energy to form images of the seafloor. These systems are very efficient at scanning large area for things like geologic formation, fish habitat, mines, ship/plane wrecks, etc. The image below (left) show the principle of operation of SLS system and the shadow created by a object on the seafloor. On the right image, we can see a typical SLS image showing a mooring block and its shadow:

<table>
<tr>
<td><img src="/assets/images/sls-shadow2.jpg" style="{height:500px;width:auto;}"/></td>
<td><img src="/assets/images/sls-image.png" style="{height:500px;width:auto;}"/></td>
</tr>
</table>

Trained human operators are usually efficient at spotting objects of interest, but SLS surveys often cover vast area and runs for days, so automating this process has become increasingly important.

### Shadow detection###

The acoustic shadows cast by objects is often easier to detect than the bright return of the object itself (the return may even be absent sometime):

![SLS image](/assets/images/sls-step1.jpg )

Due to the geometry of the problem, objects of identical size will cast different shadows depending on their distance to the sensor. Near range object will cast short shadows while far range object will cast very long shadows. So before we run any image processing algorithm, let's re-sample the image to compensate for shadow length variation (below, left):

<table>
<tr>
<td><img src="/assets/images/sls-step2.jpg"/></td>
<td><img src="/assets/images/sls-step3.jpg"/></td>
</tr>
</table>


We can see that the far range samples have lower amplitude that near range ones due to energy dispersion, so we need to normalize image across track (above, right)

If we define an approximate size for shadows of interest (green box), we can now run a match-filter to detect shadow over background area and define their bounding box(red boxes).

We read the process for highlights (object returns) to create 3 bounding boxes: shadow, object and capture area to be store on disk for further analysis:


![SLS image](/assets/images/sls-step4.png )  


Next, we'll process the capture object images to extract object measurements.

 
