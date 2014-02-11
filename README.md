lod_dump 0.1.1
========

Might and Magic 6-7-8 LOD file extractor.

- Author   : Alessandro Rosetti alessandro.rosetti@gmail.com
- License  : GPLv2 License

Comments
========
This is my first python project, I don't know the language very well.
Why? Ok there are a lot of lod extractors but none in python and 
I wanted to learn a bit of python.

Requirements
========

python3, pillow

WARNING1: sprites.lod needs .pal files (palettes) from bitmaps.lod.
          put all those files in dest/palettes/

WARNING2: currently tested on mm7, mm6 lod files. (mostly mm7),
          the script has NOT yet been tested with mm8 lod files.

Testing
========
run: ./lod_extract.py data/BITMAPS.LOD

Todo 
========
- LodManager class: handles multiple lod files using LodArchives.
                    search for files, cache of game data.
- LodArchive class: handles a single lod
- Write a Test.py that loads some res and draws the mainscreen.
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
