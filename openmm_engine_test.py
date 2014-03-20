#!/usr/bin/env python3

'''
this script has been taken from http://openglsamples.sourceforge.net/
modified to work with python3
it's an interesting example of use of openg with python
'''

import io, sys, numpy, math
from Lod import *
from Engine import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *

from PIL import Image

import threading, time

version = b'0.3.3'

tm = 0 # texmanager
lm = 0 # lodmanager
m = 0  # map
window = 0
gravity = True

sw = 1024  # glutGet(GLUT_WINDOW_WIDTH)
sh = 768
swf = float(sw) / 640.0
shf = float(sh) / 480.0

cam = 0 # camera

gobval = ('a', 'b', 'c', 'd', 'e', 'f')
gob = 0

def threadGob():
    global gob,gobval
    while True:
        time.sleep(.25)
        gob = (gob + 1) % 6

def threadInc():
    global gravity
    while True:
        time.sleep(.01)
        if gravity:
            h = (m.TerrainHeight(cam.posx, cam.posz) +
                m.TerrainHeight(cam.posx + 1, cam.posz) +
                m.TerrainHeight(cam.posx, cam.posz + 1) +
                m.TerrainHeight(cam.posx + 1, cam.posz + 1) +
                m.TerrainHeight(cam.posx - 1, cam.posz) +
                m.TerrainHeight(cam.posx, cam.posz - 1) +
                m.TerrainHeight(cam.posx - 1, cam.posz - 1) +
                m.TerrainHeight(cam.posx + 1, cam.posz - 1) +
                m.TerrainHeight(cam.posx - 1, cam.posz + 1) ) / 9
            cam.Fall(math.ceil(h))

def KeyPressed(*args):
    global gravity

    if args[0] == b'\t': # tab
        cam.DefaultPosition()

    if args[0] == b'\x1B': # escape
        sys.exit(0)

    if args[0] == b'\x7f':
        cam.Look(1)

    if args[0] == 107:
        cam.Look(0)

    if args[0] == 105:
        cam.Look(-1)

    if args[0] == b'g':
        gravity = not gravity

    if args[0] == b'a':
        cam.Rotate(1)

    if args[0] == b'd':
        cam.Rotate(-1)

    if args[0] == b'w':
        cam.Move(1)

    if args[0] == b's':
        cam.Move(-1)

    if args[0] == 104:
        cam.Fly(1)

    if args[0] == 108:
        cam.Fly(-1)

def DrawBox(x, y, z, scale):
    glBindTexture(GL_TEXTURE_2D, tm.textures["cbsm"]['id']);
    glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glPushMatrix();
    glTranslatef(x,y,z)
    glEnable(GL_DEPTH_TEST)
    glScaled(scale,scale,scale);
    glBegin(GL_QUADS);
    glTexCoord2f(0.0, 0.0); glVertex3f(-1.0, -1.0,  1.0);
    glTexCoord2f(1.0, 0.0); glVertex3f( 1.0, -1.0,  1.0);
    glTexCoord2f(1.0, 1.0); glVertex3f( 1.0,  1.0,  1.0);
    glTexCoord2f(0.0, 1.0); glVertex3f(-1.0,  1.0,  1.0);
    glTexCoord2f(1.0, 0.0); glVertex3f(-1.0, -1.0, -1.0);
    glTexCoord2f(1.0, 1.0); glVertex3f(-1.0,  1.0, -1.0);
    glTexCoord2f(0.0, 1.0); glVertex3f( 1.0,  1.0, -1.0);
    glTexCoord2f(0.0, 0.0); glVertex3f( 1.0, -1.0, -1.0);
    glTexCoord2f(0.0, 1.0); glVertex3f(-1.0,  1.0, -1.0);
    glTexCoord2f(0.0, 0.0); glVertex3f(-1.0,  1.0,  1.0);
    glTexCoord2f(1.0, 0.0); glVertex3f( 1.0,  1.0,  1.0);
    glTexCoord2f(1.0, 1.0); glVertex3f( 1.0,  1.0, -1.0);
    glTexCoord2f(1.0, 1.0); glVertex3f(-1.0, -1.0, -1.0);
    glTexCoord2f(0.0, 1.0); glVertex3f( 1.0, -1.0, -1.0);
    glTexCoord2f(0.0, 0.0); glVertex3f( 1.0, -1.0,  1.0);
    glTexCoord2f(1.0, 0.0); glVertex3f(-1.0, -1.0,  1.0);
    glTexCoord2f(1.0, 0.0); glVertex3f( 1.0, -1.0, -1.0);
    glTexCoord2f(1.0, 1.0); glVertex3f( 1.0,  1.0, -1.0);
    glTexCoord2f(0.0, 1.0); glVertex3f( 1.0,  1.0,  1.0);
    glTexCoord2f(0.0, 0.0); glVertex3f( 1.0, -1.0,  1.0);
    glTexCoord2f(0.0, 0.0); glVertex3f(-1.0, -1.0, -1.0);
    glTexCoord2f(1.0, 0.0); glVertex3f(-1.0, -1.0,  1.0);
    glTexCoord2f(1.0, 1.0); glVertex3f(-1.0,  1.0,  1.0);
    glTexCoord2f(0.0, 1.0); glVertex3f(-1.0,  1.0, -1.0);
    glEnd();
    glPopMatrix();

def DrawText(msg, x , y):
    glPushMatrix();
    #glDisable(GL_COLOR_MATERIAL)
    #glDisable(GL_LIGHTING)
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)

    off = 0
    glColor3f(1, 1, 1)
    for c in msg:
        off += 9
        glRasterPos2f(x + off, y)
        glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(c))
    glEnable(GL_TEXTURE_2D)
    glPopMatrix();

def Draw2DImage(texture, w, h, x, y):
    global swf,shf
    glPushMatrix()
    glBindTexture(GL_TEXTURE_2D, texture)
    glTranslatef(x, y, 0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0); glVertex2f(0.0, 0.0)
    glTexCoord2f(0.0, 0.0); glVertex2f(0.0, h*shf)
    glTexCoord2f(1.0, 0.0); glVertex2f(w*swf, h*shf)
    glTexCoord2f(1.0, 1.0); glVertex2f(w*swf, 0.0)
    glEnd()
    glPopMatrix()

def DrawSprite(texture, w, h, x, y, z, scale): #TODO future Sprite,SpriteManager class
    global cam
    glPushMatrix()
    glEnable(GL_DEPTH_TEST)
    glBindTexture(GL_TEXTURE_2D, texture) # this would be a texture relative to the angle between camera and sprite rotation.
    glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    r = float(h)/float(w)
    glTranslatef(x, y, z)
    glScaled(scale, scale, scale)
    glRotatef(cam.angle, 0.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    glTexCoord2f(1.0, 0.0); glVertex3f(0.0, 0.0,0.0)
    glTexCoord2f(1.0, 1.0); glVertex3f(0.0, 1.0*r,0.0)
    glTexCoord2f(0.0, 1.0); glVertex3f(1.0, 1.0*r,0.0)
    glTexCoord2f(0.0, 0.0); glVertex3f(1.0, 0.0,0.0)
    glEnd()
    glPopMatrix()

def InitGL():
    print ("Vendor:   {}".format(glGetString(GL_VENDOR).decode("utf-8")) )
    print ("Renderer: {}".format(glGetString(GL_RENDERER).decode("utf-8")) )
    print ("OpenGL Version:  {}".format(glGetString(GL_VERSION).decode("utf-8")) )
    print ("Shader Version:  {}".format(glGetString(GL_SHADING_LANGUAGE_VERSION).decode("utf-8")) )

    glClearDepth(1.0)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glDepthFunc(GL_LESS) # LEQUAL
    glShadeModel(GL_SMOOTH) # FLAT
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

def Set2DMode():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glViewport(0, 0, sw, sh)
    glOrtho(0, sw, sh, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glEnable (GL_BLEND)
    glBlendFunc ( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def SetMiniMapMode():
    global sw,sh
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    w = 270
    glViewport(sw-w, sh-w, w, w)
    gluPerspective(60.0, 1, 1, 512*250)
    gluLookAt( 0.0, 20000.0, 0.8,
               0.0, 0.1, 0.0,
               0.0, 1.0, 0.0 );
    glTranslatef(-cam.posx, 0.0, -cam.posz)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)

def Set3DMode(w,h):
    global sw,sh

    glClearDepth(1.0)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glViewport(0, h, sw - w, sh-h)
    gluPerspective(45.0, float(sw) / float(sh), 1, 512*250)
    cam.SetCamera()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity();
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    '''
    lightAmbient = [0.2, 0.3, 0.6, 1.0]
    lightDiffuse = [0.2, 0.3, 0.6, 1.0]
    lightPosition = [0,1000,600,1]

    glEnable(GL_LIGHTING);
    glLightfv(GL_LIGHT0, GL_AMBIENT,lightAmbient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightDiffuse)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPosition)
    glEnable(GL_LIGHT0)
    '''

def Render():
    global m,swf,shf
    global gobval,gob

    max_w = int((tm.textures["border1.pcx"]['w']) * swf)
    max_h = int((tm.textures["footer"]['h'] + tm.textures["border2.pcx"]['h'] - 5) * shf)
    Set3DMode(max_w, max_h)

    m.Draw()

    DrawBox(-2000, m.TerrainHeight(-1000, 1000)+10,1500, 90)
    t = tm.textures["gobfi{}0".format(gobval[gob])]
    DrawSprite(t['id'], t['w'], t['h'], -1000.0, m.TerrainHeight(-1000, 1000)+10,1000, 512 )

    SetMiniMapMode()
    m.Draw() # TODO do no re-render the map like this...

    Set2DMode()

    t = tm.textures["footer"]
    Draw2DImage(t['id'], t['w'], t['h'],
                0.0,
                (sh - shf*(float(tm.textures["border2.pcx"]['h']+t['h'] - 5)) ) )

    t = tm.textures["border2.pcx"] # bug in pillow-2.3.0 for odd sized images, fixed in git version.
    Draw2DImage(t['id'], t['w'], t['h'], 0.0, sh - shf*float(t['h']))

    t = tm.textures["border1.pcx"]
    Draw2DImage(t['id'], t['w'], t['h'],
               (sw-swf*float(t['w'])) , (sh - shf*float(t['h'])) )

    t = tm.textures["border3"]
    Draw2DImage(t['id'], t['w'], t['h'], 0.0, 0.0)

    t = tm.textures["border4"]
    Draw2DImage(t['id'], t['w'], t['h'], 0.0, 0.0)

    t = tm.textures["tap2"]
    Draw2DImage(t['id'], t['w'], t['h'], sw - swf*float(t['w']), 0.0)

    t = tm.textures["malea01"]
    Draw2DImage(t['id'], t['w'], t['h'], swf*22.0, shf*383.0)

    t = tm.textures["eradcate"]
    Draw2DImage(t['id'], t['w'], t['h'], swf*135.0, shf*383.0) # distance ~113px

    DrawText("pos ({0:.2f},{1:.2f},{2:.2f}) ang ({3:.2f} {4:.2f})".format(cam.posx, cam.posy, cam.posz, cam.angle, cam.angle2),
             18, sh - shf*(tm.textures["border2.pcx"]['h'] + 5))

    glutSwapBuffers()

def main():
    global window
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(sw, sh)
    glutInitWindowPosition(600, 300)
    window = glutCreateWindow(b'Openmm Engine Demo v ' + version )
    glutDisplayFunc(Render)
    glutIdleFunc(Render)
    glutKeyboardFunc(KeyPressed) # glutKeyboardUpFunc
    glutSpecialFunc(KeyPressed)
    InitGL()

    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    global lm, tm
    lm = LodManager()
    lm.LoadLods('data')
    tm = TextureManager(lm)
    #tm.LoadTexture ("icons", "mm6title.pcx")
    tm.LoadTexture ("bitmaps", "cbsm")
    tm.LoadTexture ("icons", "border1.pcx")
    tm.LoadTexture ("icons", "border2.pcx")
    tm.LoadTexture ("icons", "border3")
    tm.LoadTexture ("icons", "border4")
    tm.LoadTexture ("icons", "tap2", (255,0,0)) # specific alpha color
    tm.LoadTexture ("icons", "footer")
    tm.LoadTexture ("icons", "eradcate")
    tm.LoadTexture ("icons", "malea01")
    tm.LoadTexture ("sprites08", "gobfia0", True) # true get first pixel for alpha
    tm.LoadTexture ("sprites08", "gobfib0", True)
    tm.LoadTexture ("sprites08", "gobfic0", True)
    tm.LoadTexture ("sprites08", "gobfid0", True)
    tm.LoadTexture ("sprites08", "gobfie0", True)
    tm.LoadTexture ("sprites08", "gobfif0", True)

    global m
    if len(sys.argv) > 1:
        m = OdmMap("out{}.odm".format(sys.argv[1]), lm, tm)
    else:
        m = OdmMap("oute3.odm", lm, tm)

    global cam
    cam = Camera()

    t1 = threading.Thread(target=threadInc)
    t1.daemon = True
    t1.start()

    t2 = threading.Thread(target=threadGob)
    t2.daemon = True
    t2.start()

    glutMainLoop()

if __name__ == "__main__":
    print("Press 'ESC' to quit")
    print("Press 'g' to togle gravity")
    main()
