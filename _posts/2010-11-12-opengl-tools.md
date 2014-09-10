---
title: Tools for OpenGL
layout: post
---

OpenGL and its ES variant dominates the mobile  market and Unix world, but the situation on Windows platform is clearly in favor of Direct3D. From the outside, OpenGL still has the cross-platform advantage, but from a developer perspective OpenGL desktop has become a second class citizen in term of video driver quality, et productivity tools. AMD and NVIDIA do offer so tools but my experience with these have been mixed:

- RenderMonkey ATI/AMD (shader development) is being phased out.
- GPU PerfStudio 2 (AMD): VERY limited support for OpenGL. Very unstable.
- NVIDIA NSight: Actively developed and new features are added regularly, but many features are D3D only
- GLSL Devil: VERY unstable.  

If you are used to developing Direct3D app from the comfort of Microsoft Visual Studio, switching to OpenGL development may feel like a step back.
 
###Shader Compiler:###

Compiling GLSL shaders at runtime means that you need to run your app just to get compilation errors. This is very slow and frustrating. What you want -really- is  to compile shader code as part of you regular project just like the D3D shader compiler does. Unfortunately, you will have to write this tool  yourself using the OpenGL API. Not very hard, just one more thing to maintain. If you prefer Python, [Pyglet](http://www.pyglet.org/) OpenGL wrapper is the easiest to work with from my experience.

In Visual Studio, you may then setup your glsl files to "custom build" using your tool/script. If you reformat the GLSL compiler errors to [Visual Studio format](http://blogs.msdn.com/b/msbuild/archive/2006/11/03/msbuild-visual-studio-aware-error-messages-and-message-formats.aspx), they will show in your task list and clicking on a error will highlight the specific line in the glsl code.  
Unfortunately, GSLS compiler errors formatting is vendor specific so we need handle this.

Also, GLSL has no <code>#include</code> directive so it usually a good idea to write your own basic pre-processor to avoid duplicating common functions in multiple shader files. 

###API Calls debugging ###

One very nice thing about D3D is the quality of the error messages you get from the API (Use <code>D3D11\_CREATE_DEVICE\_DEBUG </code> flag in <code>D3D11CreateDevice()</code>).  OpenGL is more evasive: If you're lucky <code>glGetError()</code> will give you a <code>GL\_INVALID\_ENUM, GL\_INVALID\_VALUE, GL\_INVALID\_OPERATION</code> to think about. Getting an undocumented  error code for a specific call is not unheard of. Due to the way the OpenGL state-machine works, you may have to check quite a bit of setup calls before you figure out what went wrong. 

The easiest way to do this is to print out the call log, but for it to useful, we need the ubiquitous GLenum parameters to print as strings (what is 0x84C0 again?). Fortunately the (large) Open GL API is [available in XML format](https://cvs.khronos.org/svn/repos/ogl/trunk/doc/registry/public/api/gl.xml) so we can use python to generate some C headers for us. GL calls are wrapped into <code>glGetError()</code> checks and -as an option- print function with GLenum expanded to strings. We use macros to make sure these checks are not included in the Release Build. 

###Math Library###

There are several options for 3D math libraries, but I have found [OpenGL Mathematics](http://http://glm.g-truc.net/)(glm in short) to be very convenient and straight-forward. GLM follows the GLSL conventions and functionalities so there is basically no learning curve and GLSL documention can be used as reference.

###Mesa 3D###

OpenGL is not included on recent Windows Platform, so we must rely on a video driver being installed on target computers. We may use [ANGLE](https://code.google.com/p/angleproject/) if OpenGL ES 2.0 API is sufficient and DirectX 9 hardware is available. Otherwise, [Mesa3D with LLVMPipe](http://www.mesa3d.org/llvmpipe.html) may be an option for a  efficient software rendering fallback. Mesa3D "replaces" the vendor driver so your OpenGL App is not impacted beyond scaling down rendering complexity if needed. 
LLVMpipe is surprisingly fast for a CPU based implementation and (mostly) support OpenGL 3.0 and GLSL 1.4. There are caveats too: 

- No anisotropic filtering (due to patents)
- Single-threaded (running 2 separate contexts in two seperated threads is not safe). LLVM 3.x is can be multi-threaded and some work has been done in Mesa to leverage this, but from my experience, it's not there yet.
- Support for older CPU may be sketchy. LLVMpipe may not be tested with older CPU architecture so Mesa+LLVM combinaison may not work. Also, getting a valid build on Windows is a bit involved...  
- No docs. You have the code and that's it. Franckly, LLVMpipe code is not the most straight-forward code to read 


		
		  
          






 
 

 