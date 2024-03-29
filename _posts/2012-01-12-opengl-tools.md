---
title: Tools for OpenGL
layout: post
---

OpenGL and its ES variant dominate the mobile  market and Unix world, but the situation on Windows platform is clearly in favor of Direct3D. From the outside, OpenGL still has the cross-platform advantage, but from a developer perspective OpenGL desktop has become a second class citizen in term of video driver quality, and productivity tools. AMD and NVIDIA do offer some tools but I've had mixed luck with them:

- RenderMonkey ATI/AMD (shader development) is being phased out.
- GPU PerfStudio 2 (AMD): very limited support for OpenGL. Very unstable.
- NVIDIA NSight: Actively developed and new features are added regularly, but many of them are D3D only.
- GLSL Devil: very unstable.  

If you are used to developing Direct3D apps from the comfort of Microsoft Visual Studio, switching to OpenGL development may feel like a step back.
 
###Shader Compiler:###

Compiling GLSL shaders at runtime means that you need to run your app just to get compilation errors. This is very slow and frustrating. What you really want instead is to compile shader code as part of you regular project, just like the D3D shader compiler does. Unfortunately, you will have to write this tool yourself using the OpenGL API. Not very hard, but still one more thing to maintain. If you prefer Python, the [Pyglet](http://www.pyglet.org/) OpenGL wrapper is the easiest to work with from my experience.

In Visual Studio, you may then setup your glsl files to "custom build" using your tool/script. If you reformat the GLSL compiler errors to [Visual Studio format](http://blogs.msdn.com/b/msbuild/archive/2006/11/03/msbuild-visual-studio-aware-error-messages-and-message-formats.aspx), they will show in your task list, and clicking on a error will highlight the specific line in the glsl code.  
Unfortunately, GSLS compiler error formatting is vendor specific, so we need handle this.

Also, GLSL has no <code>#include</code> directive, so it is usually a good idea to write your own basic pre-processor to avoid duplicating common functions in multiple shader files. 

###API Calls debugging ###

A very nice thing about D3D is the quality of the error messages that you get from the API (Using <code>D3D11\_CREATE\_DEVICE\_DEBUG </code>flag in <code>D3D11CreateDevice()</code>).  OpenGL is more vague: If you're lucky <code>glGetError()</code> will give you a <code>GL\_INVALID\_ENUM, GL\_INVALID\_VALUE, GL\_INVALID\_OPERATION</code> to think about. Getting an undocumented error code for a specific call is not unheard of. Due to the way the OpenGL state-machine works, you may have to check quite a bit of setup calls before you figure out what went wrong. 

The easiest way to do this is to print out the call log, but for it to useful, we need the ubiquitous GLenum parameters to print as strings (what is 0x84C0 again?). Fortunately the (large) Open GL API is [available in XML format](https://cvs.khronos.org/svn/repos/ogl/trunk/doc/registry/public/api/gl.xml) so we can use Python to generate C headers for us. The generated code injects <code>glGetError()</code> checks and log functions with GLenum expanded to strings when needed. We use macros to make sure these checks are not included in the Release Build. 

###Math Library###

There are several options for 3D math libraries, and I have found [OpenGL Mathematics](http://http://glm.g-truc.net/) (glm in short) to be very convenient and straight-forward. GLM follows the GLSL conventions and functionalities, so there is basically no learning curve, and GLSL documentation can be used as reference.

###Mesa 3D###

OpenGL is not included on recent Windows Platform, so we must rely on a video driver being installed on target computers. We may use [ANGLE](https://code.google.com/p/angleproject/) if OpenGL ES 2.0 API is sufficient and DirectX 9 hardware is available. Otherwise, [Mesa3D with LLVMPipe](http://www.mesa3d.org/llvmpipe.html) may be an option for a  efficient software rendering fallback. Mesa3D "replaces" the vendor driver so your OpenGL App is not impacted beyond scaling down rendering complexity if needed. 
LLVMpipe is surprisingly fast for a CPU based implementation and (mostly) supports OpenGL 3.0 and GLSL 1.4. There are a few caveats: 

- No anisotropic filtering (due to patents)
- Single-threaded (running 2 separate contexts in two seperated threads is not safe). LLVM 3.x can be multi-threaded and some work has been done in Mesa to leverage this, but from my experience, it's not there yet.
- Support for older CPUs is sometimes sketchy. LLVMpipe is not always tested with older CPU architectures so the Mesa+LLVM combination doesn't always work. Also, getting a valid build on Windows is a bit involved.  
- No docs. You get the code and that's it. LLVMpipe code is not the easiest to read... 


		
		  
          






 
 

 