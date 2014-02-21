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
        logging.config.fileConfig(os.path.join("conf", "log.conf"))
        self.log = logging.getLogger('LOD')
        self.textures = {}
        self.max_texture_id = 1
        self.lm = lm # lodmanager

    def GetNewTextureId(self): # just for now.. , mutex
        self.max_texture_id = self.max_texture_id + 1
        return self.max_texture_id

    def ReleaseTexture(self, name):
        glDeleteTextures( 1, texture[name]['id'] ) # checks
        pass

    def LoadAtlasTexture(self, tex_name, dirname, imglist, trcol, trimg): #TODO join implementation with LoadTexture
        self.log.info("Loading megatexture \"{}\"".format(tex_name))
        self.log.info("max: {}".format(GL_MAX_TEXTURE_SIZE))
        texture_id = self.GetNewTextureId()
        ret = self.lm.GetLod("bitmaps").GetAtlas(imglist)

        img = ret['img']
        width = img.size[0]
        height = img.size[1]
        img = img.convert("RGBA")


        ret2 = self.lm.GetLod("bitmaps").GetFileData("", trimg)
        imgt = 0
        if ret2.get('img_size') is not None:
            imgt = Image.new("P", ret2['img_size'])
            imgt.putdata(ret2['data'])
            imgt.putpalette(ret2['palette'])
            imgt = imgt.convert("RGBA")

        if trcol is not None:
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    p = img.getpixel((x, y))
                    if set(p) == set((trcol[0], trcol[1], trcol[2], 255)):
                        img.putpixel((x, y), imgt.getpixel((x%imgt.size[0], y%imgt.size[1])))

        image  = img.tobytes("raw", "RGBA", 0, -1)

        glBindTexture     ( GL_TEXTURE_2D, texture_id )
        glPixelStorei     ( GL_UNPACK_ALIGNMENT,1 )
        glTexParameterf   ( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
        glTexParameterf   ( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
        glTexParameteri   ( GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER, GL_NEAREST ) #NEAREST
        glTexParameteri   ( GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER, GL_NEAREST ) #any combo
        gluBuild2DMipmaps ( GL_TEXTURE_2D, GL_RGBA, width, height, GL_RGBA, GL_UNSIGNED_BYTE, image )

        # TODO check if name already exists
        self.textures[tex_name] = { 'id': texture_id, 'dir': dirname,
                                    'w': width, 'h': height,
                                    'hstep': ret['hstep'] }
        return True

    def LoadTexture (self, dirname, sfile, trcol=None):
        self.log.info("Loading \"{}/{}\"".format(dirname, sfile))
        ret = self.lm.GetLod(dirname).GetFileData("", sfile) # use try, get rid of ""
        texture_id = self.GetNewTextureId()
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

        if trcol is not None and trcol != False: # I have to find a better way.. too slow
            if trcol == True:
                t = img.getpixel((0, 0))
            else:
                t = trcol
            self.trcol = t
            #data = numpy.array(img)
            #r, g, b, a = data.T
            #t_areas = (r == t[0]) & (b == t[2]) & (g == t[1])
            #data[3][t_areas] = 0
            #data[..., :-1][t_areas] = (0, t[0], t[1], t[2])
            #img = img.fromarray(data)
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
        glTexParameteri   ( GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST_MIPMAP_NEAREST ) #any combo
        gluBuild2DMipmaps ( GL_TEXTURE_2D, GL_RGBA, width, height, GL_RGBA, GL_UNSIGNED_BYTE, image )

        self.textures[sfile] = {'id': texture_id, 'dir': dirname,
                               'w': width, 'h': height}
        return True
