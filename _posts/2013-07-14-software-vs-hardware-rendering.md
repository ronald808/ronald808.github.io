---
layout: post
title: "Hardware vs. Software Rendering"
---

Hardware accelerated rendering used to be almost exclusively associated with 3D Games and Computer-Aided Design (CAD) software. Things changed with the mobile revolution. Good touch interfaces must be ultra responsive with slick animations but must draw as little power has possible.  Performance per Watt clearly favored GPU over CPU solution so OpenGL ES took hold in the mobile segment event for 2D rendering (Android 3.0+, Windows Phone 7+, Sailfish OS)

Interestingly, the desktop world was also evolving away from software rendering starting with Windows Vita. Windows 8 -with a strong focus on mobile platforms- now accelerates[ core 2D APIs](http://blogs.msdn.com/b/b8/archive/2012/07/23/hardware-accelerating-everything-windows-8-graphics.aspx) so more applications would automatically benefit from hardware acceleration without additional development cost. Linux Desktop is following suit with [Wayland](http://wayland.freedesktop.org/) and [Ubuntu's Mir](http://unity.ubuntu.com/mir/). Web Browsers  too, including Chrome and IE are accelerating more and more of the 2D work.

####The cost of Hardware Acceleration####

Hardware accelerated software is much more expensive to develop for several reasons:

#####1) Fragmentation #####

Software renderers targeting the x86 architure benefit from a mature and unified environment. Valid x86 code will run everywhere and produce a consistent output. Graphic developers face a more challenging landscape with several competing architectures (Intel GMA/HD, NVidia, AMD/ATI, ARM licensees) and complex video drivers. In addition, each successive generation of GPU offers different level of features including vendor specific extensions (CUDA, OpenGL extensions, Mantle)

While hardware vendors needs to differentiate their products, software developers need to target the widest possible audience. Doing so usually means more coding -like multiple code paths based on detected hardware capabilities- and more testing (Video Driver Versions x GPU generations x Vendors = a LOT of testing)

#####2) Driver support#####
3D Api such as OpenGL and Direct9D were created to reduce fragmentation by creating a common abstraction layer. Unfortunately, the quality of the video drivers tends to vary: On Windows, more resource are spent on D9D drivers than their OpenGL counterpart and Intel's Drivers have been plagued by quality issues for years.

The example of Google's Chrome web browser illustrate the OpenGL situation : in order to get consistent results for a "mainstream" application like Chrome for Windows, Google had to develop [Angle](https://code.google.com/p/angleproject/) to translate OpenGL ES API calls to Direct9D 9 (OpenGL ES driver may not installed on some Windows machine). In addition, Chrome -[just like FireFox]("https://wiki.mozilla.org/Blocklisting/Blocked_Graphics_Drivers")- maintains a blacklist of broken video drivers to gracefully disable hardware acceleration if a buggy driver is spotted...

   
#####3) Tools and Debugging ####
Some time ago, I wrote a short article on [development tools for OpenGL]({% post_url 2012-01-12-opengl-tools %}) describing some of the difficulties encountered when coding and debugging hardware accelerated code. These range from API complexity, shader code debugging, unexpected software fallback by the driver, etc.

#####4) Software Fallback####
If your code need to run everywhere, you will need to develop a software implementation to take over the accelerated code path when some minimum conditions are not met. And this will happen: Virtual machines or remote desktop environments usually do not support hardware acceleration and old hardware may be to expensive to accelerate anyway. Obviously, the extra work adds to the cost of the final product.

### Mainstream GPUs ###

For user to benefit from accelerated code, they need a GPU and this is where the advent of CPU integrated GPU have changed everything. For several CPU generations, Intel and AMD have dedicated more and more silicon real estate to graphic acceleration. 
Like floating-point co-processors before them, GPUs will become widespread enough that developer could just rely on them to be there. They may reduce fragmentation and thus development cost by providing mainstream GPU support. 


