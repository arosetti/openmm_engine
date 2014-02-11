import sys, os
import logging, logging.config
from Lod.LodArchive import LodArchive
import shutil

class LodManager(object):
    '''Multiple lod archive class'''
   
    def __init__(self):
        logging.config.fileConfig('conf/log.conf')
        self.log = logging.getLogger('LOD')
        self.lod_list = []

    def Load(self, filename):
        self.log.info('''Adding "{}"'''.format(os.path.basename(filename)))
        l = LodArchive(filename)
        if l.loaded:
            self.lod_list.append(l)
        else:
            self.log.info('''Loading "{}" failed'''.format(os.path.basename(filename)))
    
    def LoadDir(self, path):
        try:
            lods = [fn for fn in os.listdir(path) if any([fn.lower().endswith('.lod')])];

            for lod in lods:
                self.Load(os.path.join(path,lod))
            self.LoadPalettes()
        except Exception as err:
            self.log.error("{}".format(err))

    def LoadPalettes(self):
        dest = "tmp/palettes"
        if not os.path.exists(dest):
            os.makedirs(dest)
        for l in self.lod_list:
            if l.lod_attr['dirname'] == "bitmaps":
                l.SaveFiles(dest, "pal")
