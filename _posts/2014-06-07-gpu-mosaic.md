---
title: "Remote Sensing Mosaic using the GPU" 
layout: post
---

A lot of remote sensing application involve creating maps from raw sensor data either in real-time or in post-processing. In this article we will focus on *rasters*, uniform 2D grids of cells such as images and elevation grids.
{{excerpt_separator}}
The chart below illustrate the general process of turning raw sensor data into rasters:

![ rasterize chart]( {{site.baseurl}}/assets/images/rasterize-chart.png)


"Processing" and "rasterization" are the most computationally intensive steps so offloading these tasks to a GPU could be very advantageous:

- **Real-time**: Enable on-the-fly mapping of high-resolution data
- **Post-processing**: Re-processing maps quickly to boost productivity 


### Example: Forward Looking Sonar (FLS) ###

A forward looking sonar is an "acoustic flash-light" that will insonify the seabed to create a image off the reflected sound waves. FLS systems generate many images per second so when mounted on a moving platform they become an powerful tool to map underwater region in zero visibility.

In the case of a FLS, GPU acceleration is highly desirable as we need to generate a map in real-time despite high data-rates (~8 million sample/sec) and non-trivial processing. 

**Data Format and Geocoding**   
To create an accurate map, we need to now how to interpret each sample from the sensor, calculate its position and place it on a raster. Data usually consist of a 2-D array of 16 bit amplitude samples in polar coordinate:

![ Sector FLS](/assets/images/sector-shape.png)

Meta-data such as longitude, latitude and heading of the platform will allow us to compute the position of each data frames (sector image)

**GPU: Vertex Transform**

First step is to turn our rectangular array of sample into a sector-shaped image. The GPU can do this very efficiently by texture-mapping our rectangular array over a sector-shaped mesh of triangle:

![Mesh](/assets/images/fls2d-mesh.png)


The mesh consists of a single strip for rendering performance. Degenerated triangles (left-to-right lines on the image above) used to create a single strip will not render when texture mapping the sector.  

To avoid elongated triangles, we space vertexes along the range dimension to form (almost) isosceles triangles:  

<a href="http://www.codecogs.com/eqnedit.php?latex=\left\{\begin{matrix}&space;r_{n-1}&space;=1.0&space;&&space;i=0\\&space;r_{n-i-1}&space;=&space;r_{n-i}-min(&space;d_{min},&space;2*sin(&space;\frac{d\theta}{2}))&space;&&space;i&space;\in&space;[1,n-1],&space;&&space;r_{n-i}>=r_{min}>=0;&space;\end{matrix}\right." target="_blank"><img src="http://latex.codecogs.com/gif.latex?\left\{\begin{matrix}&space;r_{n-1}&space;=1.0&space;&&space;i=0\\&space;r_{n-i-1}&space;=&space;r_{n-i}-min(&space;d_{min},&space;2*sin(&space;\frac{d\theta}{2}))&space;&&space;i&space;\in&space;[1,n-1],&space;&&space;r_{n-i}>=r_{min}>=0;&space;\end{matrix}\right." title="\left\{\begin{matrix} r_{n-1} =1.0 & i=0\\ r_{n-i-1} = r_{n-i}-min( d_{min}, 2*sin( \frac{d\theta}{2})) & i \in [1,n-1], & r_{n-i}>=r_{min}>=0; \end{matrix}\right." /></a>

*d&theta;* is the angular increment chosen for the mesh. 

As the sensor moves and rotate between frames, we will need to recompute the position of the vertexes in the mesh for every frame. Ideally we would like the GPU perform these computations to free up the CPU. To do so, we will load a unit grid mesh to the GPU and displace its vertexes in a vertex shader to form a sector of the proper range, arc, orientation and position.

![]( /assets/images/multi-frame.png )
![]( /assets/images/multi-frame-textured.png )

*note: frame are artificially spaced to show degenerated triangles. See below for original frame position:*

![]( /assets/images/multi-frame-stacked.png )


To optimize the rasterization process, we batch multiple frame together to render them at once. To create a single triangle strip, we connect the frame meshes with degenerated triangles. We pack the frame data into a single texture and store per-frame meta-information into a float texture so we don't have the repeat meta-data for each vertexes.



**GPU: Beam mapping**

Unfortunately, some FLS do not create equi-angular beams (i.e.beams spacing is not constant across the arc). As a consequence, texture-mapping the data directly on the mesh would not be accurate. Here too, the GPU can help and provide an efficient solution: we will use a 1-D texture to implement the beam-mapping function: u<sub>actual</sub> = F(u<sub>linear</sub>)

{}

**GPU: Frame Feathering**     

As we can see on the images below, frame-to-frame transition are somewhat distracting, so we would like to introduce some blending at the edge of the frames to create a seamless raster.


{ no feathering}


{with feathering}


To support alpha-blending, we add a transparency channel to our raster so we now have two 16-bit channels {amplitude, transparency}. We implement feathering in the pixel shader using a <code>smoothstep()</code> function around the edge of each frame. 

	// HLSL : Pixel Shader
	[...]
	// input.Tex: normalized interpolated polar coordinate in [0,1]
	float2 	c_feather = float2( 0.1, 0.15 ); //in [0,1] (0.0: no feathering)
	float2 alpha	= smoothstep(float2(0.0, 0.0), c_feather, input.Tex) * (float2(1.0, 1.0) - 
					smoothstep( 1.0 - c_feather, float2(1.0, 1.0), input.Tex));
	output.a		= max(alpha.x * alpha.y, 0.05);
	[...]

![]( /assets/images/multi-frame-feathering.png )

### GPU Rasterizer ###

The area covered by the sensor may be large, we should not assume that our raster will fit in video memory. In real-time we may not even now which area will be surveyed, so we need to come up with a dynamic way of managing our raster. Special care must also be taken when blending new frame over previously mapped data. 
To achieve this, we will re-define our raster as an expending grid of tiles. We will add tiles to the raster as the area covered by the sensor expends. If the new frames overlap existing non-empty tiles, we will load these background tiles first:

1. New batch of frame loaded to GPU 
1. Render pass to compute **actual** "tile footprint" of the batch (i.e. which background tiles will be updated, which new tile will be created)
2. Load *missing* (and not empty!) background tile to GPU tile cache
3. Place background tile from tile cache to render target
4. Render the batch on render target
5. Save "changed" tiles back to render target 

![]( /assets/images/rasterize-diag.png)


    
At the implementation level, the tile cache is simply a texture array (say 4 slice of 8x8 tiles of 256<sup>2</sup> texels) coupled with a Least Recently Used (LRU) caching system to evict the "oldest" tile when room is needed for the newly mosaic data. Evicted tile will be store on disk and stream back to GPU when needed.

Depending on the rendering needs [see article on raster rendering](), we may  task the GPU with creating level-of-detail (mipmaps) of the tiles before we read them back to system memory.


