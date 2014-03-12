import sys, struct, math

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import logging, logging.config
import pprint

class Camera(object):
    '''Camera class'''

    def __init__(self):
        logging.config.fileConfig(os.path.join("conf", "log.conf"))
        self.log = logging.getLogger('LOD')
        
        self.fall = 1
        self.rot_step = 8
        self.mov_step = 512*0.25
        self.DefaultPosition()

    def ValidPosition(self, ex, ez, ey):
        l = 44*512
        return ( -l < ex < l ) and ( -l < ez < l ) and (0 < ey < l/4)

    def DefaultPosition(self):
        self.angle = 130.0
        self.angle2 = 10.0
        self.posx = 0
        self.posy = 3000
        self.posz = 0
        self.lx = math.sin(math.radians(-self.angle))
        self.lz = -math.cos(math.radians(-self.angle))
        self.ly = math.sin(math.radians(-self.angle2))
    
    def Move(self, sign):
        assert(sign == 1 or sign == -1)
        ex = self.posx + sign * self.mov_step * self.lx
        ez = self.posz + sign * self.mov_step * self.lz
        if self.ValidPosition(ex, ez, self.posy):
            self.posx = ex
            self.posz = ez

    def Rotate(self, sign): # +1,-1
        assert(sign == 1 or sign == -1)
        self.angle = (self.angle + sign * self.rot_step) % 360
        self.lx = math.sin(math.radians(-self.angle))
        self.lz = -math.cos(math.radians(-self.angle))

    def Fly(self, sign):
        assert(sign == 1 or sign == -1)
        ey = self.posy + sign * self.mov_step / 2
        if self.ValidPosition(self.posx, self.posz, ey):
            self.posy = ey

    def Look(self, sign):
        self.angle2 = (self.angle2 - sign * self.rot_step) % 360
        if sign == 1:
            if 100 < self.angle2 < 300:
                self.angle2 = 300
        elif sign == -1:
            if 80 < self.angle2 < 99:
                self.angle2 = 80
        else:
            angle2 = 10
  
        self.ly = math.sin(math.radians(-self.angle2))

    def Fall(self, h):
        if (self.posy - 450) > h:
            self.fall += 1
            self.posy -= self.fall
        else:
            self.fall = 1
            self.posy = h + 450

    def SetCamera(self):
        gluLookAt(self.posx, self.posy, self.posz,
                  self.posx + self.lx, self.posy + self.ly, self.posz + self.lz,
                  0.0, 1.0, 0.0)
