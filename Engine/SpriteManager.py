import sys, struct, math

from Engine import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from PIL import Image

import logging, logging.config
import pprint

def get_filename(data):
    chunks = data.split(b'\x00')
    tmp = "{0}".format(chunks[0].decode('latin-1'))
    return tmp

class SpriteManager(object):
    '''Sprite class'''

    def __init__(self, tm, hm):
        logging.config.fileConfig(os.path.join("conf", "log.conf"))
        self.log = logging.getLogger('LOD')
        self.tm = tm
        self.scale = 32
        self.LoadSprites(['bush01','tree01'])
        
        self.sprite_map = numpy.empty(128,128)
        self.height_map = hm
        

    def LoadSprites(self, sprites):
        self.log.info("building sprites")
        for s in sprites:
            tm.LoadTexture ("bitmaps", s['name'], True)
    
    def Draw(self):
        glBindTexture(GL_TEXTURE_2D, self.tm.textures[self.tex_name]['id'])
        glPushMatrix()
            
        glPopMatrix()
   
    def Draw(texture, angle):
        for sprite in self.sprites:
            glPushMatrix()
            glEnable(GL_DEPTH_TEST)
            glBindTexture(GL_TEXTURE_2D, texture) # this would be a texture relative to the angle between camera and sprite rotation.
            r = float(sprite['h'])/float(sprite['w'])
            glTranslatef(sprite['x'], sprite['y'], sprite['z'])
            glScaled(self.scale, self.scale, self.scale)
            glRotatef(angle, 0.0, 1.0, 0.0)
            glBegin(GL_QUADS)
            glTexCoord2f(1.0, 0.0); glVertex3f(0.0, 0.0,0.0)
            glTexCoord2f(1.0, 1.0); glVertex3f(0.0, 1.0*r,0.0)
            glTexCoord2f(0.0, 1.0); glVertex3f(1.0, 1.0*r,0.0)
            glTexCoord2f(0.0, 0.0); glVertex3f(1.0, 0.0,0.0)
            glEnd()
            glPopMatrix()

    def DrawAxis(self):
        pass
