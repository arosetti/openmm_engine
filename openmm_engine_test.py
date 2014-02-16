#!/usr/bin/env python3

'''
this script has been taken from http://openglsamples.sourceforge.net/
modified to work with python3
it's an interesting example of use of openg with python
'''

import io, sys, math, numpy

from Lod import *
from Engine import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

import threading, time

sky_rot = 0.0

def threadInc():
    global sky_rot
    while True:
        time.sleep(.01)
        sky_rot = (sky_rot + 0.007) % 360.0

tm = 0 # texmanager
lm = 0 # lodmanager
window = 0

sw = 1024
sh = 768
swf = float(sw) / 640.0
shf = float(sh) / 480.0

#rotation
x_axis = 0.0
y_axis = 0.0
z_axis = 0.0
direction = 1
angle = 0
camx = -3.0
camz = 2.0
camy = 0.0

# define a matrix 
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

def keyPressed(*args):
    global x_axis,y_axis,z_axis
    global camx,camy,camz,angle
    
    rot_step = 7
    mov_step = 0.8

    if args[0] == b'\033': # escape
        sys.exit()

    if args[0] == b'a':
        y_axis = y_axis - rot_step;

        angle = (angle - rot_step) % 360
    if args[0] == b'd':
        y_axis = y_axis + rot_step;
        angle = (angle + rot_step) % 360


    if args[0] == b'w':
        camx += math.sin(math.radians(-angle))*mov_step
        camz += math.cos(math.radians(-angle))*mov_step

    if args[0] == b's':
        camx -= math.sin(math.radians(-angle))*mov_step
        camz -= math.cos(math.radians(-angle))*mov_step

    if args[0] == b'q':
        camy += math.sin(math.radians(-angle))*mov_step

    if args[0] == b'e':
        camy -= math.sin(math.radians(-angle))*mov_step


def DrawBox():
    glBindTexture(GL_TEXTURE_2D, tm.textures["cbsm"]['id']);
    glPushMatrix();
    glTranslatef(3.0,-.5,-3.0)
    glScaled(.4,.4,.4);
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
    glScaled(100,100,100);
    glPushMatrix();
    glTranslatef(0,0,0)
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
    l = 0.007
    l2 = 0.0085
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
    glPopMatrix();

def DrawText(msg):
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

    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)

def Draw2DImage(texture, w, h, x, y):
    glBindTexture(GL_TEXTURE_2D, texture)
    glPushMatrix();
    glTranslatef(x,y,0);
    glBegin(GL_QUADS);
    glTexCoord2f(0.0, 1.0); glVertex2f(0.0, 0.0);
    glTexCoord2f(0.0, 0.0); glVertex2f(0.0, h*shf);
    glTexCoord2f(1.0, 0.0); glVertex2f(w*swf, h*shf);
    glTexCoord2f(1.0, 1.0); glVertex2f(w*swf, 0.0);
    glEnd();
    glPopMatrix();

def InitGL():
    glClearColor(0.1, 0.1, .7, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS) # LEQUAL
    glShadeModel(GL_SMOOTH)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

def Set2DMode():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity();
    glOrtho(0, sw, sh, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glEnable (GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)

def Set3DMode():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(sw) / float(sh), .1, 3000)
    gluLookAt(0, 0, .5, 0, 0, 0, 0.0, 1.0, 0.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity();
    glEnable(GL_TEXTURE_2D)

    glEnable (GL_BLEND)
    glBlendEquation(GL_FUNC_ADD)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0)
    #glEnable(GL_LIGHTING)
    #glDisable(GL_COLOR_MATERIAL)

def SetCamera():
    glRotatef(x_axis,1.0,0.0,0.0)
    glRotatef(y_axis,0.0,1.0,0.0)
    glRotatef(z_axis,0.0,0.0,1.0)
    glTranslatef(camx,camy,camz)

def Render():
    global x_axis,y_axis,z_axis
    global direction
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    Set3DMode()
    SetCamera()

    DrawDungeon()
    DrawBox()
    DrawSky()
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

    DrawText("position ({0:.2f},{1:.2f},{2:.2f}) angle {3:.2f}".format(camx,camy,camz,angle))

    glutSwapBuffers();

def main():
    global window
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(sw,sh)
    glutInitWindowPosition(200,200)

    window = glutCreateWindow(b'Openmm_engine test')

    global lm 
    lm = LodManager()
    lm.LoadLods('data')
    global tm
    tm = TextureManager(lm)

    tm.LoadTexture ("bitmaps", "bemob2b") # wall
    tm.LoadTexture ("bitmaps", "d2ceil4") # ceil
    tm.LoadTexture ("bitmaps", "bcsctr")  # floor
    tm.LoadTexture ("bitmaps", "cbsm")
    tm.LoadTexture ("bitmaps", "sky07")

    tm.LoadTexture ("icons", "border1.pcx")
    tm.LoadTexture ("icons", "border2.pcx")
    tm.LoadTexture ("icons", "border3")
    tm.LoadTexture ("icons", "border4")
    tm.LoadTexture ("icons", "tap2", (255,0,0))
    tm.LoadTexture ("icons", "footer")

    tm.LoadTexture ("icons", "eradcate")
    tm.LoadTexture ("icons", "malea01")

    glutDisplayFunc(Render)
    glutIdleFunc(Render)
    glutKeyboardFunc(keyPressed)
    InitGL()

    t = threading.Thread(target=threadInc)
    t.daemon = True
    t.start()

    glutMainLoop()

if __name__ == "__main__":
    main() 
