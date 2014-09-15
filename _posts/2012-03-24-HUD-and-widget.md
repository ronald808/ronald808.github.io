---
title: Semi-transparent widgets over a 3D Viewport
layout: post
---

3D applications often have a 2D overlay to display information in screen space. This head-Up Display (HUD) may be drawn directly from the 3D App:

1. Render 3D content (Perspective Projection)
2. Setup Ortho projection for screen-space drawing.
3. Render 2D HUD content

![Head Up Display](/assets/images/hud-view.png)

### Simple Head-Up Display (HUD)###

When the HUD does not require user inputs and simple UI elements are needed, we may draw them directly: 

- Icons, frames and decoration may just be images stored in a texture atlas and render over quads in pixel coordinate
- Text elements may require a high-level library if you need many fonts type/size combination, paragraph layout or strong unicode support. On the other end, for simple elements, you could also choose to deal with text rendering yourself using [FreeType](http://www.freetype.org) or an OS-dependent equivalent. Textual overlay is usually broken down into “dynamic” text (e.g.numbers) and “static text” (labels, warning, info, etc.). 
	- For static text, we rasterize the entire text to a image and add it to our texture atlas.
	- For dynamic text, we usually render each "glyph" in our character set to a dedicated texture atlas and then texture-quad each glyph on screen to create the text label. Rendering can be pretty efficient since we can combine all characters into a single triangle trip connected with degenerated triangle and render them within a single draw call. Using a mono-spaced font may simplifies the implementation   


### A need for Widgets ###

For a lot of applications, the HUD includes control widgets such as sliders, radio buttons, check boxes, lists, combo-boxes, etc.
Implementing these GUI components, composition and event system is time consuming, so ideally we'd like to use a library for that. Mature widget libraries such as WPF or Qt are perfect for the task. 

In addition, support for a transparent background is a must for a successful widget-based HUD. As illustrated on the screenshots below, opaque HUD (right)  may block too much of the view compare to transparent HUD (left) to be useful.

<table><tr><td>
<img src="/assets/images/hud-transparency-3.png"/>
</td><td>
<img src="/assets/images/hud-transparency-2.png"/>
</td></tr></table>


### Transparency and the "airspace" issue ###
Unfortunatly, most GUI tookits do not support transparency over 3D surface.  While disappointing, it is easy to see why: GUI tookits rendering system doesn't have access to our OpenGL/D3D surface so it can't use it to fill the widgets background before rendering the widgets with alpha-blending. Yes, in theory, we could do a read-back of the 3D scene buffer and use this as our HUD background. In most case, this requires a GPU to CPU readbacks which are notoriously slow and are guaranteed to kill performances.

- **WPF** is a bit of an exception here since WPF rendering engine is hardware accelerated under most conditions (WDDM, D3D 9 on Vista+). WPF expose a D3DImage that will allow us to skip the dreaded GPU to CPU readback and maintain good performances... unless you're using D3D 11, in which case you'll need to jump through more loops to get there.
- On the **Qt** side, a quick glance at the docs offers hope: Looks like we should be able to get a paintEngine instance from our QGLWidget, create a QPainter with it and proceed to render our HUD widgets. Yes, QPaintEngine has a openGl implementation; yes you can overlay triangle, lines and quads all you want, but no, it won't draw widgets correctly, at least not in Qt 4.8.  A little bit of digging into Qt/Digia forums confirm the bad news: it just won't work. 

### Widgets and transparency ###
  
Well, we could go for an OpenGL Widget toolkit such as CEGUI or MiniGUI, but the integration complications (and rendering glitches) make these options unpalatable.

We may still be able achieve transparency using Qt re-targeted painting. Conceptually we'd like to have our HUD widget behave like regular widgets, but "paint" them in OpenGL so that transparency may be possible (Our 3D scene with show through tranparent/semi-transparent pixels). 

The key to achieve this is to turn on the QWidget <code> Qt::WA_DontShowOnScreen</code> attribute on our parent HUD widget. This "Ghost" widget will behave as a "regular" widget but won't paint. We may now:

![Qt HUD with transparency diagram](/assets/images/hud-transparency-1.png)

1. Re-target the rendering to a pixmap ( *with* transparency!) within <code>QWidget::paintEvent()</code> 
2. Copy this pixmap to a texture on the 3D side. 
3. Create a "proxy" texured-quad in the OpenGL HUD scene with the same size/position as our "Ghost" QWidget  
3. We can now have a transparent background for our widget, control alpha-blending and do any pixel transformation we like in the pixel/fragment shader !


In term of performance, rendering a widget to a pixmap doesn't have additional cost and texturing a quad on the GPU side is very fast, so the main overhead is in the GPU->CPU load operation and video memory usage. With the exception of dynamic label and animations, most HUD widgets only need to be updated in response to mouse/keyboard events so we won't be updating the texture too frequently in most cases. 


