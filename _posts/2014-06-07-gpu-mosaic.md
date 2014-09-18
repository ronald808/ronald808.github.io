---
title: "Remote Sensing Mosaic using the GPU" 
layout: post
---

The purpose of many remote sensing applications is to create rasters: 2D arrays of samples such as images or elevation maps. A generic work flow may look like this:
 

<img src= "{{site.baseurl}}/assets/images/rasterize-chart.png" style="{height:100px}"/>
 

*"Processing"* and *"rasterization"* are computationally intensive steps which usually slow-down the post-processing and rasterization of data. For on-the-fly visualization apps, processing performance becomes even more critical to keep up with incoming data. In this article, we will explore how we can use the computing power of Graphical Processing Units (GPU) to speed up raster creation.

### Example: Forward-Look Sonar (FLS) ###

A forward-look sonar is an "acoustic flash-light" which insonifies the seabed to derives an image from the reflected sound waves. FLS systems generate several images per second, so when they are mounted on a moving platform they become an powerful tool to map underwater region in zero visibility.

![fls mosaic]({{site.baseurl}}/assets/images/fls-mosaic3.png)

FLS mosaics are a good candidates for GPU acceleration since we may have to rasterize over 8 million samples per second.

![fls mosaic]({{site.baseurl}}/assets/images/samm-screenshot.jpg)

####Data Format and Geocoding####

To create an accurate map, we need to know how to interpret every sample from the sensor, calculate their position and place them on a raster. The sector data usually consists of a 2-D array of 16-bit amplitude sampled in polar coordinates:

![ Sector FLS]({{site.baseurl}}/assets/images/sector-shape.png)

Meta-data such as longitude, latitude and heading of the platform will allow us to geocode each sector image and add it to our raster mosaic.

####Vertex Displacement (Vertex Shader)####

The first step is to turn our rectangular array of samples into a sector-shaped image. The GPU can do this very efficiently by texture-mapping our rectangular array over a sector-shaped mesh of triangles:

<!--
<table>
<tr>
<td><img src="{{site.baseurl}}/assets/images/fls2d-mesh.png"/><td>
<td><img src="{{site.baseurl}}/assets/images/fls-textured-sector.jpg"/></td>
</tr>
</table>
-->
![Mesh]({{site.baseurl}}/assets/images/fls2d-mesh.png)
![Mesh]({{site.baseurl}}/assets/images/fls-textured-sector.jpg)

Degenerated triangles (horizontal lines on the image above) connect rows of triangles into a single triangle strip for rendering performance. Degenerated triangles will be discarded by the GPU when rendering the texture-mapped sector.

To avoid elongated triangles, we space vertexes along the range dimension to form (almost) isosceles triangles:  

<!--
<img src="http://latex.codecogs.com/gif.latex?\left\{\begin{matrix}&space;r_{n-1}&space;=1.0&space;&&space;i=0\\&space;r_{n-i-1}&space;=&space;r_{n-i}-min(&space;d_{min},&space;2*sin(&space;\frac{d\theta}{2}))&space;&&space;i&space;\in&space;[1,n-1],&space;&&space;r_{n-i}>=r_{min}>=0;&space;\end{matrix}\right." />
-->
![equation]({{site.baseurl}}/assets/images/equation-1.gif)

*d&theta;* is the angular increment chosen for the mesh. 

As the sensor moves and rotates between frames, we need to recompute the real world position of the vertexes in the mesh for every frame. Ideally, we would like the GPU to perform these computations to free up CPU cycles. To do so, we load a unit (rectangular) grid mesh into a vertex buffer and displace its vertexes directly within the vertex shader to form the sector mesh shown above.

<table>
<tr>
<td><img src="{{site.baseurl}}/assets/images/multi-frame.png"/></td>
<td><img src="{{site.baseurl}}/assets/images/multi-frame-textured.png" /></td>
</tr>
</table>

*note: frames are artificially spaced to show degenerated triangles. Image below shows actual (overlapping) frame positions:*

![]( /assets/images/multi-frame-stacked.png )


To optimize the rasterization process, we group multiple frames together to render them at once. Using the same degenerated-triangle technique as described above, we connect the grouped meshes together and render them efficiently in a single draw-call.  We pack sensor data for the grouped framed into a single texture and compute texture coordinates accordingly. Finally, we also group per-frame info (sensor position, heading, arc, etc) into a float texture for vertex displacement computation in the shader. This saves video memory since we do not have to repeat these meta-data per vertex.


####Beam Mapping with 1-D Texture (Pixel Shader)####

Unfortunately, some FLS do not create equi-angular beams (i.e.beam spacing is not constant across the arc) so linear texture-mapping would not map samples correctly. Here too, the GPU can help and provide an efficient solution: we use a 1-D texture to implement the beam-mapping function: u<sub>actual</sub> = F(u<sub>linear</sub>)

![]( {{site.baseurl}}/assets/images/beam-angle-plot-small.png )

In the pixel shader, we apply the correction function to the y-texture coordinate before texture look-up.


####Frame Feathering (Pixel Shader)####

As we can see on the images below, frame-to-frame transition can be distracting (right), so we would like to introduce some blending at the edge of the frames to create a seamless raster (left):

<table>
<tr>
<td><img src="{{site.baseurl}}/assets/images/fls-feathering-off.jpg"/></td>
<td><img src="{{site.baseurl}}/assets/images/fls-feathering-on.jpg"/></td>
</tr>
</table>

To implement alpha-blending, we add a transparency channel to our raster so we now have two 16-bit channels {amplitude, transparency}. We implement feathering in the pixel shader using a <code>smoothstep()</code> function around the edge of each frame. 

{% highlight c %}
// HLSL : Pixel Shader
[...]
// input.Tex: normalized interpolated polar coordinate in [0,1]
float2 	c_feather = float2( 0.1, 0.15 ); //in [0,1] (0.0: no feathering)
float2 alpha	= smoothstep(float2(0.0, 0.0), c_feather, input.Tex) * (float2(1.0, 1.0) - 
				smoothstep( 1.0 - c_feather, float2(1.0, 1.0), input.Tex));
output.a		= max(alpha.x * alpha.y, 0.05);
[...]
{% endhighlight %}

Which creates the following frame-feathering (white: opaque, magenta: fully transparent):

![]( /assets/images/multi-frame-feathering.png )

### GPU Rasterizer (Direct 3D) ###

Since the survey area may be large, we can't assume that our mosaic will fit in video memory. In an on-the-fly rendering scenario, we may not even know upfront which area will be covered, so we need to manage our raster dynamically. Additionally, the  data structure should allow blending new frames over previously mapped data. With this in mind, we define our raster mosaic as an expending grid of fixed-size tiles. We add tiles to the raster as the area covered by the sensor expends:

1. Load new batch of frames to GPU 
1. Render pass to compute **actual** "tile footprint" of the batch (i.e. which background tiles will be updated?, which new tile will be created?)
2. Load *missing* (colliding AND not empty!) background tiles to GPU tile cache
3. Place background tile from tile cache to the render target
4. Render the batch on the render target
5. Save "changed" tiles back to the tile buffer 

![]( /assets/images/rasterize-diag.png)

    
At the implementation level, the tile cache is simply a texture array (such as 4 slices of 8x8 tiles of 256<sup>2</sup> texels) coupled with a Least Recently Used (LRU) caching system to evict the "oldest" tiles when room is needed for the newly mosaicked data. Evicted tiles are flushed to disk but will be streamed back to GPU when needed.

Depending on the rendering needs, we may task the GPU with creating level-of-detail (mipmaps) of the tiles before we read them back to system memory. My previous article [on raster rendering]({% post_url 2013-12-05-gpu-gis %}) details how to use the GPU to render our raster efficiently. 


