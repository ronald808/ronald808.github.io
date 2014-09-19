---
layout: post
title: Objects Detection in  Sonar Images
---

Side-looking sonars transmit acoustic pulses, and record the back-scattered energy to form images of the seafloor. These systems are very efficient at scanning large areas for things like geologic formations, fish habitats, mines, ship/plane wrecks, etc. The image below (left) shows the concept of operation of an SLS system with the acoustic shadow of an object lying on the seafloor. On the right image, we can see a typical SLS image showing a mooring block and its shadow:

<table>
<tr>
<td><img src="/assets/images/sls-shadow2.jpg" style="{height:500px;width:auto;}"/></td>
<td><img src="/assets/images/sls-image.png" style="{height:500px;width:auto;}"/></td>
</tr>
</table>

Trained human operators are very efficient at spotting objects of interest, but SLS surveys often run for days and cover such large areas that automating this process has become increasingly important.

### Shadow detection###

The acoustic shadow cast by an object is often easier to detect than the bright return of the object itself (the return may even be absent sometimes):

![SLS image](/assets/images/sls-step1.jpg )

Due to the geometry of the problem, objects of identical size will cast different shadows depending on their distance from the sensor. Near range objects cast shorter shadows, while far range objects cast longer ones. So before we run any image processing algorithm, we re-sample the image to compensate for shadow length variations:

<table>
<tr>
<td><img src="/assets/images/sls-slant-flip-compress.jpg"/></td>
<td><img src="/assets/images/sls-step2-boxes.jpg"/></td>
</tr>
</table>

The shadow-length normalized image (right) provides a more accurate representation of the dimension of the shadows we wish to detect. As you can see, far range samples have been “compressed” whereas the nadir samples have been allocated more pixels in the resulting image.

Due to energy dispersion, samples amplitude decreases with the range so we need to normalize image across track before we run our detection filter:

<td><img src="/assets/images/sls-step3.jpg"/></td>

If we define an approximate size for shadows of interest (green box in the top-left corner), we can now run a match-filter to detect a shadow signature (red boxes).

We use a similar process for highlights (object returns) to create 3 bounding boxes: shadow (red), object (cyan) and capture area (yellow):


![SLS image](/assets/images/sls-step4.png )  



Before we measure contacts, we need to geode them so that their shape and orientation are accurate. Width and length can be measured directly while height can be inferred from shadow-length using simple trigonometry. To do so, we use an active contour detection algorithm (also called "snake" algorithms). Yellow boxes show the initial "seed" areas and red contours represent the final results after convergence:

 ![Active contour]({{site.baseurl}}/assets/images/targets_4x2_activecontour.png )


###Contact Database###

After automatic measurement, contacts are stored to a database. Depending on the application, contacts may then be reviewed by a human operator or feed to a vector support machine for classification (man-made objects, geology features, etc.)

<table>
<tr>
<td><img src="/assets/images/contact-browser.png"/></td>
<td><img src="/assets/images/contact-browser2.png"/></td>
</tr>
</table>
  