openmm_engine v0.3.3
========

Might and Magic 6-7-8 engine attempt.

- Author   : Alessandro Rosetti alessandro.rosetti@gmail.com
- License  : GPLv2 License

[[Second Youtube video]](https://www.youtube.com/watch?v=HxxwzMQU_LI)

[[First Youtube video]](http://www.youtube.com/watch?v=w5J2rvrX_14)

![ScreenShot](/res/screen_road_to_castle_ironfist.png)

Requirements
========

- python3
- pillow
- pyopengl
- numpy

WARNING: lod classes tested on mm6,7,8 a few files are still failing to be extracted.

WARNING2: this program is being developed on linux. It's not currently being ever tested on other systems.

Testing
========
Put the "data" directory containing lod files in the same directory of the scripts and create a tmp directory.

You can play with the class methods, extract all data or search specific files.
- run: ./lod_test.py
       ./map_test.py

MM6 Opengl Engine Demo
----------
This is a simple opengl demo. It loads resources from the original MM6 lod files :D

(the original opengl code has been taken from http://openglsamples.sourceforge.net/ and adapted to my needs)

WARNING: use data from MM6! (tested on gentoo linux)
- run: ./openmm\_engine\_test.py \<mapcode\>

Mapcode is a 2 char coordinate of the map of Enroth.
The first char is one of (a b c d e). The second char is one of (1 2 3).
For example 'e3' is new New Sorpigal which is default if you don't specify the parameter.

The keyboard is mapped to the movement system of MMVI. wasd, pag up,down ins...etc.
use g to togle gravity on and off.
That's really bad for a laptop, sorry for now...

as you can see the map is not yet completed.

![ScreenShot](/res/new_sorpigal.png)

rudimental sprite display and with animation of a goblin

![ScreenShot](/res/screen_ui.png)

Todo
========
- LodManager class: cache of game data, create new lod files, other helpful functions.
- LodArchive: Threadsafe Lod* class ?
- GUI class:  buttons, decorators, animations etc...
- SndArchive class: snd files.
- 3D engine.... this hurts.
- The game logic ... take me to the temple please.

Comments
========
This is one of my first python projects.

Don't be shocked if you find the code horrorific, I don't know the language very well. ( I know C/C++ )

Why am I doing this?
There are a lot of lod extractors but none in python and I wanted to learn a bit of this magnificent language.

I'm doing this work for fun contact me if you want to help ;)

The current work is very very raw and there is no actual engine but mostly tests of modules, random code.

As soon as I see that the work is possible I hope to be able to clean the code and use a better architecture!

I found very helpful the documentations and the code of other projects like mm_mapview, mm8leveleditor, mm7view, and the new mm7 reverse engineering.
also this link: http://rewiki.regengedanken.de/wiki/Might_and_Magic_6


Insane future works (sure, dream on... :P)
========
- FULL python/c implementation of 3DO's Might and Magic engine for mm6-7-8 and mods.
- new adventures from scratch!
- redo all 2.5D sprites to 3D models.
- better buildings/objects models, bump mapping stuff like that...

Disclaimer
========
I own these games, if you want to use this script buy the games. look at gog.com or ebay..
All trademarks, product names are the property of their respective owners!
