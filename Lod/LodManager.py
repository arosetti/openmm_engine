import sys, os
import logging, logging.config
from Lod.LodArchive import *
import shutil

class LodManager(object):
    '''Multiple lod archive class'''
   
    def __init__(self):
        logging.config.fileConfig('conf/log.conf')
        self.log = logging.getLogger('LOD')
        self.lod_list = []

    def LoadLod(self, filename):
        self.log.info('''Adding "{}"'''.format(os.path.basename(filename)))
        l = LodArchive(filename)
        if l.loaded:
            self.lod_list.append(l)
        else:
            self.log.info('''Loading "{}" failed'''.format(os.path.basename(filename)))

    def LoadLods(self, path):
        try:
            lods = [fn for fn in os.listdir(path) if any([fn.lower().endswith('.lod')])];

            for lod in lods:
                self.LoadLod(os.path.join(path,lod))
            self.SetupPalettes()
        except Exception as err:
            self.log.error("{}".format(err))

    def GetLod(self, dirname):
        for l in self.lod_list:
            if l.lod_attr['dirname'] == dirname:
                return l
        return None

    def SetupPalettes(self):
        lod_bitmaps = self.GetLod("bitmaps")
        palettes = {}

        for p in lod_bitmaps.GetFileList("pal"):
            ret = lod_bitmaps.GetFileData("", p)
            if len(ret['data']) == PAL_SIZE:
                palettes.update({p: ret['data']})
        for l in self.lod_list:
            l.palettes = palettes
