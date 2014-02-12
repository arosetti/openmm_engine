openmm_engine 0.3
========

Might and Magic 6-7-8 engine, LOD file extractor.

- Author   : Alessandro Rosetti alessandro.rosetti@gmail.com
- License  : GPLv2 License

Comments
========
This is my first python project, I don't know the language very well.

Why?
Ok there are a lot of lod extractors but none in python and 
I wanted to learn a bit of python.

I'm doing this work for fun contact me if you want to help ;)
The current work is very raw and there are mostly tests of modules to build 
the actual engine.

Requirements
========

- python3, pillow

- WARNING: tested on mm6,7,8 but a few files are still failing to be extracted.
- WARNING2: this program is being developed on linux. if you are a windows user you may have to change it a bit.

Testing
========
You can play with the class methods, extract all data or search specific files.
- run: ./lod_test.py

This is a simple example opengl with python3 that loads resources from lod files
and uses as textures for walls and floor. :D
(code taken from http://openglsamples.sourceforge.net/ and adapted to my needs)

WARNING: use data from mm6! (tested on gentoo linux)
- run: ./openmm_engine_test.py

![ScreenShot](/res/screen.png)

Todo 
========
- LodManager class: handles multiple lod files using LodArchives.
                    search for files, cache of game data.
- Threadsafe Lod* class ?
- Read/Write new Lod archives from scratch.
- Write a test_draw.py that loads some res and draws the mainscreen.
- GUI class:
  buttons
  decorators.
  etc...
- SndArchive class: snd files.
- Animation of sprites and gif-like img.
- 3D engine.... this hurts.
- The actual game logic ... take me to the temple please.

Insane future works
========
(sure, dream on... :P)
python/c implementation of 3DO's Might and Magic engine.

new adventures from scratch!
support for mods.
redo all 2.5D sprites to 3D models.
better buildings/objects models, bump mapping stuff...

Disclaimer
========
I own these games, if you want to use this script buy the games. look at gog.com
All trademarks, product names are the property of their respective owners!
