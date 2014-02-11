#!/usr/bin/env python3
from Lod import *
import pprint

dest = "tmp"

l = LodArchive('data/BITMAPS.LO') # this call is going to fail
l = LodArchive('data/BITMAPS.LOD')

l.SaveFile(dest, "non_existent_file")
l.SaveFile(dest, "sky17")
l.SaveFiles(dest, "sky")
l.SaveFiles(dest, "pal")

l2 = LodArchive('data/SPRITES.LOD')
l2.SaveFiles(dest, "tree")

print(l.GetFileList("sky0"))
print(l2.GetFileList("gobf"))

