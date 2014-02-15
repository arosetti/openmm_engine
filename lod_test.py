#!/usr/bin/env python3
from Lod import *
import pprint

dest = "tmp"

lm = LodManager()
lm.LoadLods('data')

lod_sprites = lm.GetLod("sprites08")
if lod_sprites is not None:
    lod_sprites.SaveFiles(dest, "tree")
else:
    print("can't find sprites08")

lod_icons = lm.GetLod("icons")
if lod_icons is not None:
    lod_icons.SaveFiles(dest, "border")
    lod_icons.SaveFiles(dest, "footer")
    lod_icons.SaveFiles(dest, "tap")
    lod_icons.SaveFiles(dest, "pcx")
else:
    print("can't find sprites08")
