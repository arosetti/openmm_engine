#!/usr/bin/env python3
from Engine import *
from Map import *
from Lod import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

dest = "tmp"

global window
glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
glutInitWindowSize(640,480)
glutInitWindowPosition(200,200)
window = glutCreateWindow(b'Openmm_engine test')

lm = LodManager()
lm.LoadLods('data')
tm = TextureManager(lm)
m = MMap("outa1.odm", lm, tm)
