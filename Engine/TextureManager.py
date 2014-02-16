import sys, os
import io, math, numpy
from Lod import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

import logging, logging.config

class TextureManager(object):
    '''Texture loading and rendering class'''
   
    def __init__(self, lm):
        logging.config.fileConfig('conf/log.conf')
        self.log = logging.getLogger('LOD')
        self.textures = {}
        self.max_texture_id = 1
        self.lm = lm # lodmanager

    def GetTextureId(self): # just for now.. , mutex
        self.max_texture_id = self.max_texture_id + 1
        return self.max_texture_id

    def ReleaseTexture(self, name):
        glDeleteTextures( 1, texture[name]['id'] ) # checks
        pass

    def LoadTexture (self, dirname, sfile, transparency_color=None):
        ret = self.lm.GetLod(dirname).GetFileData("", sfile) # use try, get rid of ""
        texture_id = self.GetTextureId()
        
        width = 0
        height = 0
        if ret.get('img_size') is not None:
            width  = ret['img_size'][0]
            height = ret['img_size'][1]
            img = Image.new("P", ret['img_size'])
            img.putdata(ret['data'])
            img.putpalette(ret['palette'])
        else:
            fdata = io.BytesIO(ret['data'])
            img = Image.open(fdata)
            width = img.size[0]
            height = img.size[1]
            #print("{} {},{}".format(ret['name'], width, height))

        img = img.convert("RGBA")

        if transparency_color is not None:
            t=transparency_color
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    p = img.getpixel((x, y))
                    if set(p) == set((t[0], t[1], t[2], 255)):
                        img.putpixel((x, y), (p[0], p[1], p[2], 0))

        image  = img.tobytes("raw", "RGBA", 0, -1)
        glBindTexture     ( GL_TEXTURE_2D, texture_id )   
        glPixelStorei     ( GL_UNPACK_ALIGNMENT,1 )
        glTexParameterf   ( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
        glTexParameterf   ( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
        glTexParameteri   ( GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST ) #NEAREST
        glTexParameteri   ( GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST_MIPMAP_LINEAR ) #any combo
        gluBuild2DMipmaps ( GL_TEXTURE_2D, 3, width, height, GL_RGBA, GL_UNSIGNED_BYTE, image )

        self.textures[sfile] = {'id': texture_id, 'dir': dirname,
                               'w': width, 'h': height}
        return True
