#!/usr/bin/env python3
from Lod import *
import pprint

dest = "tmp"

lm = LodManager()
lm.LoadLods('data')

lod_sprites = lm.GetLod("sprites08")
if lod_sprites is not None:
    lod_sprites.SaveFiles(dest, "tree")
    lod_sprites.SaveFiles(dest, "gob")
else:
    print("can't find sprites08")

lod_icons = lm.GetLod("icons")
if lod_icons is not None:
    lod_icons.SaveFiles(dest, "border")
    lod_icons.SaveFiles(dest, "footer")
    lod_icons.SaveFiles(dest, "tap")
    lod_icons.SaveFiles(dest, "pcx")
else:
    print("can't find icons")

lod_maps = lm.GetLod("maps")
if lod_maps is not None:
    lod_maps.SaveFiles(dest, "out")
else:
    print("can't find , maps")

lod_bitmaps = lm.GetLod("bitmaps")
if lod_bitmaps is not None:
    texlist = ['pending', 'dirttyl', 'grastyl', 'grdrtne', 'grdrtse', 'grdrtnw', 'grdrtsw', 'grdrte', 'grdrtw', 'grdrtn', 'grdrts', 'grdrtxne', 'grdrtxse', 'grdrtxnw', 'grdrtxsw', 'drsrcros', 'drsrns', 'drsrew', 'drsrn_e', 'drsrn_w', 'drsrs_e', 'drsrs_w', 'drsrns_e', 'drsrns_w', 'drsrew_n', 'drsrew_s', 'drsrncap', 'drsrecap', 'drsrscap', 'drsrwcap', 'drrdcros', 'drrdns', 'drrdew', 'drrdn_e', 'drrdn_w', 'drrds_e', 'drrds_w', 'drrdns_e', 'drrdns_w', 'drrdew_n', 'drrdew_s', 'drrdncap', 'drrdecap', 'drrdscap', 'drrdwcap']
    print(len(texlist))
    lod_bitmaps.GetJoinedImgs(texlist)
else:
    print("can't find , bitmaps")
