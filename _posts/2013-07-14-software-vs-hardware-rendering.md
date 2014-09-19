---
layout: post
title: "Hardware vs. Software Rendering"
---

Hardware accelerated rendering used to be almost exclusively associated with 3D games and Computer-Aided Design (CAD) software. Things changed with the mobile revolution. Ultra responsive touch interfaces with slick animations must draw as little power has possible. Performance per Watt clearly favored GPU over CPU solution, and OpenGL ES took hold of the mobile segment even for 2D rendering (Android 3.0+, Windows Phone 7+, Sailfish OS)

Interestingly, starting with Windows Vita, the desktop world has also been evolving away from software rendering. Windows 8 -with a strong focus on mobile platforms- now accelerates[ core 2D APIs](http://blogs.msdn.com/b/b8/archive/2012/07/23/hardware-accelerating-everything-windows-8-graphics.aspx), and more applications benefit from hardware acceleration without additional development cost. Linux Desktop is following suit with [Wayland](http://wayland.freedesktop.org/) and [Ubuntu's Mir](http://unity.ubuntu.com/mir/). Web browsers, including Chrome and IE, are also accelerating more and more of the 2D work.

####The cost of Hardware Acceleration####

Hardware accelerated software is much more expensive to develop for several reasons:

#####1) Fragmentation #####

Software renderers targeting the x86 architecture benefit from a mature and unified environment. Valid x86 code will run everywhere and produce a consistent output. Developers face a more challenging landscape with several competing architectures (Intel GMA/HD, NVidia, AMD/ATI, ARM licensees) and complex video drivers. In addition, each successive generation of GPU offers different levels of features, including vendor specific extensions (CUDA, OpenGL extensions, Mantle).

While hardware vendors need to differentiate their products, software developers need to target the widest possible audience. Doing so usually means more coding (with different execution paths based on detected hardware capabilities) and more testing (Video Driver Versions x GPU generations x Vendors = a LOT of testing).

#####2) Driver support#####
3D Apis such as OpenGL and Direct9D were created to reduce fragmentation by creating a common abstraction layer. Unfortunately, the quality of the video drivers tends to vary: On Windows, more resources are spent on D9D drivers than with their OpenGL counterpart, and Intel's drivers have been plagued with quality issues for years.

Google Chrome illustrates the OpenGL situation. In order to get consistent results for a "mainstream" applications such as Chrome for Windows, Google had to develop [Angle](https://code.google.com/p/angleproject/) to translate OpenGL ES API calls to Direct9D 9 (some Windows machines may not have the OpenGL ES driver installed). In addition, Chrome -[like FireFox]("https://wiki.mozilla.org/Blocklisting/Blocked_Graphics_Drivers")- maintains a blacklist of broken video drivers to gracefully disable hardware acceleration if a buggy driver is spotted...

   
#####3) Tools and Debugging ####
Some time ago, I wrote a short article on [development tools for OpenGL]({% post_url 2012-01-12-opengl-tools %}), describing some of the difficulties encountered when coding and debugging hardware accelerated code. These range from API complexity, shader code debugging, unexpected software fallback by the driver, etc.

#####4) Software Fallback####
If your code needs to run everywhere, you will need to develop a software implementation that can take-over the accelerated code path when some minimum conditions are not met. This is likely to happen. Virtual machines or remote desktop environments usually do not support hardware acceleration, and old hardware may be too expensive to accelerate anyway. The extra work adds to the cost of the final product.

### Mainstream GPUs ###

For users to benefit from accelerated code, they need a GPU. This is where the advent of CPU integrated GPU have changed everything. For several CPU generations, Intel and AMD have dedicated more and more silicon real estate to graphic acceleration. Like floating-point co-processors did before them, GPUs will become widespread enough that developers can just expect them to be there. Integrated GPUs will reduce fragmentation and thus development cost by providing mainstream GPU support. 


