#!/usr/bin/env python3

'''
this script has been taken from http://openglsamples.sourceforge.net/
modified to work with python3
it's an interesting example of use of openg with python
'''

import io, sys, numpy, math
from Lod import *
from Engine import *
from Map import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

import threading, time

tm = 0 # texmanager
lm = 0 # lodmanager
m = 0  # map
window = 0
status = 3

status_lock = threading.Lock()


sw = 1024  # glutGet(GLUT_WINDOW_WIDTH)
sh = 768
swf = float(sw) / 640.0
shf = float(sh) / 480.0

#camera
angle = 90.0
angle2 = 15.0
eyex = -1260
eyey = 4864
eyez = -1555
lx = math.sin(math.radians(-angle))
lz = -math.cos(math.radians(-angle))
ly = math.sin(math.radians(-angle2))

sky_rot = 0.0

gobval = ('a', 'b', 'c', 'd', 'e', 'f')
gob = 0

def ReadStatus():
    global status,status_lock
    status_lock.acquire()
    val = status
    status_lock.release()
    return val

def WriteStatus(val):
    global status,status_lock
    status_lock.acquire()
    status = val
    status_lock.release()

def threadGob():
    global sky_rot,gob,gobval
    while True:
        time.sleep(.25)
        gob = (gob + 1) % 6

def threadInc():
    global sky_rot
    while True:
        time.sleep(.01)
        sky_rot = (sky_rot + 0.007) % 360.0

def keyPressed(*args):
    global eyex,eyey,eyez,angle,angle2
    global lx,lz,ly

    rot_step = 0
    mov_step = 0
    st = ReadStatus()
    if st == 2:
        rot_step = 5
        mov_step = .5
    elif st == 3:
        rot_step = 5
        mov_step = 512*0.5

    if args[0] == b'\t': # escape
        angle = 0
        angle2 = 15
        if st == 3:
            eyex = 2.0
            eyey = 0.7
            eyez = 4.0
            WriteStatus(2)
        elif st == 2:
            eyex = -1260
            eyey = 4864
            eyez = -1555
            WriteStatus(3)

    if args[0] == b'\x1B': # escape
        sys.exit(0)

    if args[0] == b'\x7f':
        angle2 = (angle2 + rot_step) % 360
        ly = math.sin(math.radians(-angle2))

    if args[0] == 107:
        angle2 = 15
        ly = math.sin(math.radians(-angle2))

    if args[0] == 105:
        angle2 = (angle2 - rot_step) % 360
        ly = math.sin(math.radians(-angle2))

    if args[0] == b'a':
        angle = (angle + rot_step) % 360
        lx = math.sin(math.radians(-angle))
        lz = -math.cos(math.radians(-angle))

    if args[0] == b'd':
        angle = (angle - rot_step) % 360
        lx = math.sin(math.radians(-angle))
        lz = -math.cos(math.radians(-angle))

    if args[0] == b'w':
        eyex += mov_step * lx
        eyez += mov_step * lz

    if args[0] == b's':
        eyex -= mov_step * lx
        eyez -= mov_step * lz

    if args[0] == 104:
        eyey += mov_step

    if args[0] == 108:
        eyey -= mov_step

def DrawBox(x,y,z, scale):
    glBindTexture(GL_TEXTURE_2D, tm.textures["cbsm"]['id']);
    glPushMatrix();
    glTranslatef(x,y,z)
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

def DrawSky():
    glBindTexture(GL_TEXTURE_2D, tm.textures["sky07"]['id']);
    glPushMatrix();
    glScaled(60000,60000,60000);
    glRotatef(sky_rot, 0.0, 1.0, 0.0);
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

matrix = [[0 for i in range(10)] for j in range(10)]

matrix[0][0] = 1
matrix[0][1] = 1
matrix[0][2] = 1
matrix[0][3] = 1
matrix[0][4] = 1
matrix[0][5] = 1

matrix[1][5] = 1
matrix[2][5] = 1
matrix[3][5] = 1
matrix[4][5] = 1
matrix[5][5] = 1

matrix[5][4] = 1
matrix[5][3] = 1
matrix[5][2] = 1
matrix[5][1] = 1


matrix[1][3] = 1
matrix[2][3] = 0
matrix[3][3] = 1
matrix[4][3] = 1

def DrawDungeon():
    glPushMatrix();
    glTranslatef(-3.0,0.0,0.0)
    for numz in range(0,10):
        for num in range(0,10):
            glBindTexture(GL_TEXTURE_2D, tm.textures["bemob2b"]['id'])   # 2d texture (x and y size)
            glBegin(GL_QUADS); # floor
            glTexCoord2f(1.0, 1.0); glVertex3f(-1.0 + num*2, -1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 1.0); glVertex3f( 1.0 + num*2, -1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 0.0); glVertex3f( 1.0 + num*2, -1.0,  1.0 - numz*2);
            glTexCoord2f(1.0, 0.0); glVertex3f(-1.0 + num*2, -1.0,  1.0 - numz*2);
            glEnd();

            glBindTexture(GL_TEXTURE_2D, tm.textures["d2ceil4"]['id'])
            glBegin(GL_QUADS); # roof
            glTexCoord2f(1.0, 1.0); glVertex3f(-1.0 + num*2, 1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 1.0); glVertex3f( 1.0 + num*2, 1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 0.0); glVertex3f( 1.0 + num*2, 1.0,  1.0 - numz*2);
            glTexCoord2f(1.0, 0.0); glVertex3f(-1.0 + num*2, 1.0,  1.0 - numz*2);
            glEnd();

            glBindTexture(GL_TEXTURE_2D, tm.textures["bcsctr"]['id'])   # 2d texture (x and y size)
            if matrix[num][numz] == 1:
                glBegin(GL_QUADS);
                glTexCoord2f(0.0, 0.0); glVertex3f(-1.0 + num*2, -1.0,  1.0 - numz*2);
                glTexCoord2f(1.0, 0.0); glVertex3f( 1.0 + num*2, -1.0,  1.0 - numz*2);
                glTexCoord2f(1.0, 1.0); glVertex3f( 1.0 + num*2,  1.0,  1.0 - numz*2);
                glTexCoord2f(0.0, 1.0); glVertex3f(-1.0 + num*2,  1.0,  1.0 - numz*2);
                glTexCoord2f(1.0, 0.0); glVertex3f(-1.0 + num*2, -1.0, -1.0 - numz*2);
                glTexCoord2f(1.0, 1.0); glVertex3f(-1.0 + num*2,  1.0, -1.0 - numz*2);
                glTexCoord2f(0.0, 1.0); glVertex3f( 1.0 + num*2,  1.0, -1.0 - numz*2);
                glTexCoord2f(0.0, 0.0); glVertex3f( 1.0 + num*2, -1.0, -1.0 - numz*2);
                glTexCoord2f(0.0, 1.0); glVertex3f(-1.0 + num*2,  1.0, -1.0 - numz*2);
                glTexCoord2f(0.0, 0.0); glVertex3f(-1.0 + num*2,  1.0,  1.0 - numz*2);
                glTexCoord2f(1.0, 0.0); glVertex3f( 1.0 + num*2,  1.0,  1.0 - numz*2);
                glTexCoord2f(1.0, 1.0); glVertex3f( 1.0 + num*2,  1.0, -1.0 - numz*2);
                glTexCoord2f(1.0, 1.0); glVertex3f(-1.0 + num*2, -1.0, -1.0 - numz*2);
                glTexCoord2f(0.0, 1.0); glVertex3f( 1.0 + num*2, -1.0, -1.0 - numz*2);
                glTexCoord2f(0.0, 0.0); glVertex3f( 1.0 + num*2, -1.0,  1.0 - numz*2);
                glTexCoord2f(1.0, 0.0); glVertex3f(-1.0 + num*2, -1.0,  1.0 - numz*2);
                glTexCoord2f(1.0, 0.0); glVertex3f( 1.0 + num*2, -1.0, -1.0 - numz*2);
                glTexCoord2f(1.0, 1.0); glVertex3f( 1.0 + num*2,  1.0, -1.0 - numz*2);
                glTexCoord2f(0.0, 1.0); glVertex3f( 1.0 + num*2,  1.0,  1.0 - numz*2);
                glTexCoord2f(0.0, 0.0); glVertex3f( 1.0 + num*2, -1.0,  1.0 - numz*2);
                glTexCoord2f(0.0, 0.0); glVertex3f(-1.0 + num*2, -1.0, -1.0 - numz*2);
                glTexCoord2f(1.0, 0.0); glVertex3f(-1.0 + num*2, -1.0,  1.0 - numz*2);
                glTexCoord2f(1.0, 1.0); glVertex3f(-1.0 + num*2,  1.0,  1.0 - numz*2);
                glTexCoord2f(0.0, 1.0); glVertex3f(-1.0 + num*2,  1.0, -1.0 - numz*2);
                glEnd();
    glPopMatrix();

def DrawAxis():
    global status
    if status == 3:
        l=512
        l2=512+50
    else:
        l = 1
        l2 = 1.03
    glPushMatrix();
    glDisable(GL_COLOR_MATERIAL)
    glDisable(GL_LIGHTING)
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)
    glLineWidth(2.0);
    glBegin(GL_LINES);
    glColor3f(1,0,0);
    glVertex3f(0, 0, 0);
    glVertex3f(l, 0, 0);
    glColor3f(0,1,0);
    glVertex3f(0, 0, 0);
    glVertex3f(0, l, 0);
    glColor3f(0,0,1);
    glVertex3f(0, 0, 0);
    glVertex3f(0, 0, l);
    glEnd();

    glColor3f(1.0, 1.0, 0.2)
    glRasterPos3f(l2, 0.0, 0.0)
    glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('x'))
    glRasterPos3f(0.0, l2, 0.0)
    glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('y'))
    glRasterPos3f(0.0, 0.0, l2)
    glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('z'))
    glEnable(GL_TEXTURE_2D)
    glPopMatrix();

def DrawText(msg):
    glPushMatrix();
    glDisable(GL_COLOR_MATERIAL)
    glDisable(GL_LIGHTING)
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)
    hoff = sh - shf*(tm.textures["border2.pcx"]['h'] + 5)

    off = 0
    glColor3f(1, 1, 1)
    for c in msg:
        off += 9
        glRasterPos2f(18 + off, hoff)
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
    glEnable(GL_TEXTURE_2D)
    glPopMatrix();

def Draw2DImage(texture, w, h, x, y):
    glPushMatrix()
    glBindTexture(GL_TEXTURE_2D, texture)
    glTranslatef(x,y,0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0); glVertex2f(0.0, 0.0)
    glTexCoord2f(0.0, 0.0); glVertex2f(0.0, h*shf)
    glTexCoord2f(1.0, 0.0); glVertex2f(w*swf, h*shf)
    glTexCoord2f(1.0, 1.0); glVertex2f(w*swf, 0.0)
    glEnd()
    glPopMatrix()

def DrawSprite(texture, w, h, x, y, z, scale):
    glPushMatrix()
    glBindTexture(GL_TEXTURE_2D, texture)
    r = float(h)/float(w)
    glTranslatef(x, y, z)
    glScaled(scale,scale,scale)
    glRotatef(angle, 0.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    glTexCoord2f(1.0, 0.0); glVertex3f(0.0, 0.0,0.0)
    glTexCoord2f(1.0, 1.0); glVertex3f(0.0, 2.0*r,0.0)
    glTexCoord2f(0.0, 1.0); glVertex3f(2.0, 2.0*r,0.0)
    glTexCoord2f(0.0, 0.0); glVertex3f(2.0, 0.0,0.0)
    glEnd()
    glPopMatrix()

def InitGL():
    glClearColor(0.1, 0.1, .1, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS) # LEQUAL
    glShadeModel (GL_FLAT) #glShadeModel(GL_SMOOTH)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glFlush()

def Set2DMode():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, sw, sh, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glEnable (GL_BLEND)
    glBlendFunc ( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def Set3DMode():
    global eyex,eyey,eyez, lx,lz,ly
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50.0, float(sw) / float(sh), .1, 512*3000)
    gluLookAt(eyex, eyey, eyez,
              eyex + lx, eyey + ly, eyez + lz,
              0.0, 1.0, 0.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity();
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    #glEnable(GL_LIGHTING)
    #glDisable(GL_COLOR_MATERIAL)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def Render():
    global m
    global gobval,gob
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    st = ReadStatus()

    if st == 2 or st == 3:
        Set3DMode()
        DrawSky()

    if st == 2:
        DrawDungeon()
        DrawBox(3.0,-0.5,-3.0, .4)
        t = tm.textures["gobfi{}0".format(gobval[gob])]
        DrawSprite(t['id'], t['w'], t['h'], 12.0, -1.0, 0.0, .4 )
        DrawSprite(t['id'], t['w'], t['h'], 1.0, -1.0, -2.0, .4 )
    elif st == 3:
        m.Draw()
        DrawBox(-1352.0,2817,1444, 70)
        t = tm.textures["gobfi{}0".format(gobval[gob])]
        DrawSprite(t['id'], t['w'], t['h'], -1356.0,2809,1444, 300 )

    if st == 2 or st == 3:
        DrawAxis()
        Set2DMode()

        t = tm.textures["footer"]
        Draw2DImage(t['id'], t['w'], t['h'],
                    0.0,
                    (sh - shf*(float(tm.textures["border2.pcx"]['h']+t['h'] - 5)) ) )

        t = tm.textures["border2.pcx"] # there is a problem in pillow library for this image (fixed in git version of pillow)
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

        DrawText("pos ({0:.2f},{1:.2f},{2:.2f}) ang ({3:.2f} {4:.2f}). [TAB] toggle testroom".format(eyex,eyey,eyez,angle, angle2))

    glutSwapBuffers()

def main():
    global window
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(sw,sh)
    glutInitWindowPosition(200,200)
    window = glutCreateWindow(b'Openmm_engine test')

    global lm, tm
    lm = LodManager()
    lm.LoadLods('data')
    tm = TextureManager(lm)
    tm.LoadTexture ("icons", "mm6title.pcx")
    tm.LoadTexture ("bitmaps", "bemob2b") # wall
    tm.LoadTexture ("bitmaps", "d2ceil4") # ceil
    tm.LoadTexture ("bitmaps", "bcsctr")  # floor
    tm.LoadTexture ("bitmaps", "cbsm")
    tm.LoadTexture ("bitmaps", "sky07")
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
        m = MMap("out{}.odm".format(sys.argv[1]), lm, tm)
    else:
        m = MMap("outb1.odm", lm, tm)

    glutDisplayFunc(Render)
    glutIdleFunc(Render)
    glutKeyboardFunc(keyPressed) # glutKeyboardUpFunc
    glutSpecialFunc(keyPressed)
    InitGL()

    t1 = threading.Thread(target=threadInc)
    t1.daemon = True
    t1.start()

    t2 = threading.Thread(target=threadGob)
    t2.daemon = True
    t2.start()

    glutMainLoop()

if __name__ == "__main__": [WIP] starting work on terrain tilemap ; test now can load different maps from argv
    main() 
