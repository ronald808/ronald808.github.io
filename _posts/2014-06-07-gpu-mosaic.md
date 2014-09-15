---
title: "Remote Sensing Mosaic using the GPU" 
layout: post
---

The purpose of many remote sensing application is to create rasters: 2D arrays of samples such as images and elevation maps. How to turn sensor data into meaningful raster is application dependent be usually involves the following steps: 
 

<img src= "{{site.baseurl}}/assets/images/rasterize-chart.png" style="{height:100px}"/>
 

"Processing" and "rasterization" are computationally intensive steps which usually slow-down post-processing of data into raster products. Performance is event more of a problem if we need to create/update our rasters on the fly for real-time display purpose. 
Graphical Processing Unit (GPU) are extremely fast at certain parallel tasks so we will explore how we can tap their power to boost raster creation.

### Example: Forward-Look Sonar (FLS) ###

A forward-look sonar is an "acoustic flash-light" that will insonify the seabed to create a image off the reflected sound waves. FLS systems generate many images per second so when mounted on a moving platform they become an powerful tool to map underwater region in zero visibility.

![fls mosaic]({{site.baseurl}}/assets/images/fls-mosaic3.png)

In the case of a FLS, GPU acceleration is highly desirable as we may need to transform and rasterize over 8 million samples per seconds. 

####Data Format and Geocoding####

To create an accurate map, we need to know how to interpret each sample from the sensor, calculate its position and place it on a raster. The sector data usually consist of a 2-D array of 16 bit amplitude sampled in polar coordinate:

![ Sector FLS]({{site.baseurl}}/assets/images/sector-shape.png)

Meta-data such as longitude, latitude and heading of the platform will allow us to geocode each sector image and add it to our raster mosaic.

####GPU: Vertex Transform####

First step is to turn our rectangular array of sample into a sector-shaped image. The GPU can do this very efficiently by texture-mapping our rectangular array over a sector-shaped mesh of triangles:

![Mesh]({{site.baseurl}}/assets/images/fls2d-mesh.png)


Degenerated triangles (horizontal lines on the image above) connects triangles rows to create a single triangle strip for rendering performance.  Degenerated triangles will be discarded by the GPU when rendering the texture-mapped sector.
  

To avoid elongated triangles, we space vertexes along the range dimension to form (almost) isosceles triangles:  

<!--
<img src="http://latex.codecogs.com/gif.latex?\left\{\begin{matrix}&space;r_{n-1}&space;=1.0&space;&&space;i=0\\&space;r_{n-i-1}&space;=&space;r_{n-i}-min(&space;d_{min},&space;2*sin(&space;\frac{d\theta}{2}))&space;&&space;i&space;\in&space;[1,n-1],&space;&&space;r_{n-i}>=r_{min}>=0;&space;\end{matrix}\right." />
-->
![equation]({{site.baseurl}}/assets/images/equation-1.gif)

*d&theta;* is the angular increment chosen for the mesh. 

As the sensor moves and rotate between frames, we will need to recompute the position of the vertexes in the mesh for every frame. Ideally we would like the GPU to perform these computations to free up the CPU. To do so, we will load a unit (rectangular) grid mesh to the GPU and displace its vertexes in a vertex shader to form the sector mesh shown above.

![]( /assets/images/multi-frame.png )
![]( /assets/images/multi-frame-textured.png )

*note: frame are artificially spaced to show degenerated triangles. See below for original frame position:*

![]( /assets/images/multi-frame-stacked.png )


To optimize the rasterization process, we batch multiple frame together to render them at once. Using the same degenerated-triangles technique, we connect frame meshes together and render them in a single draw-call for efficiency. We pack the sensor data for all the frame in a batch into a single texture and store per-frame meta-information into a float texture so we don't have the repeat meta-data for each vertexes.



####GPU: Beam mapping####

Unfortunately, some FLS do not create equi-angular beams (i.e.beams spacing is not constant across the arc). As a consequence, texture-mapping the data directly on the mesh would not be accurate. Here too, the GPU can help and provide an efficient solution: we will use a 1-D texture to implement the beam-mapping function: u<sub>actual</sub> = F(u<sub>linear</sub>)

{}

####GPU: Frame Feathering####     

As we can see on the images below, frame-to-frame transition are somewhat distracting, so we would like to introduce some blending at the edge of the frames to create a seamless raster.


{ no feathering}


{with feathering}


To support alpha-blending, we add a transparency channel to our raster so we now have two 16-bit channels {amplitude, transparency}. We implement feathering in the pixel shader using a <code>smoothstep()</code> function around the edge of each frame. 

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

### GPU Rasterizer ###

Since the area covered by the sensor may be large, we should not assume that our raster will fit in video memory. In real-time we may not even now which area will be surveyed, so we need to come up with a dynamic way of managing our raster. Special care must also be taken when blending new frame over previously mapped data. 
To support this, we store our raster as an expending grid of tiles. We will add tiles to the raster as the area covered by the sensor expends. If the new frames overlap existing non-empty tiles, we will load these background tiles first:

1. New batch of frame loaded to GPU 
1. Render pass to compute **actual** "tile footprint" of the batch (i.e. which background tiles will be updated?, which new tile will be created?)
2. Load *missing* (and not empty!) background tile to GPU tile cache
3. Place background tile from tile cache to render target
4. Render the batch on render target
5. Save "changed" tiles back to render target 

![]( /assets/images/rasterize-diag.png)


    
At the implementation level, the tile cache is simply a texture array (say 4 slice of 8x8 tiles of 256<sup>2</sup> texels) coupled with a Least Recently Used (LRU) caching system to evict the "oldest" tile when room is needed for the newly mosaic data. Evicted tiles are flushed to disk and stream back to GPU when needed.

Depending on the rendering needs , we may  task the GPU with creating level-of-detail (mipmaps) of the tiles before we read them back to system memory. Please see my article [on raster rendering]({% post_url 2013-12-05-gpu-gis %}) for more detail on how to use the GPU to render our raster efficiently. 


