#!/usr/bin/env python3

'''
this script has been taken from http://openglsamples.sourceforge.net/
modified to work with python3
it's an interesting example of use of openg with python
'''

import sys, math, numpy
from Lod import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

lm = 0
window = 0
ID = 0

#rotation
X_AXIS = 0.0
Y_AXIS = 0.0
Z_AXIS = 0.0
 
DIRECTION = 1

texture  = 0
textureWall = 1
textureCube = 2
angle = 0

camx = 0
camz = 0

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

image = ""
image2 = ""

def InitGL(Width, Height): 
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0) 
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)   
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_TEXTURE_2D) # initialize texture mapping
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    
 
def keyPressed(*args):
    global X_AXIS,Y_AXIS,Z_AXIS
    global camx, camz,angle
    
    rot_step = 7
    mov_step = 0.8

    if args[0] == b'\033': # escape
        sys.exit()

    if args[0] == b'a':
        Y_AXIS = Y_AXIS - rot_step;
        angle -= rot_step

    if args[0] == b'd':
        Y_AXIS = Y_AXIS + rot_step;
        angle += rot_step

    if args[0] == b'w':
        camx += math.sin(math.radians(-angle))*mov_step
        camz += math.cos(math.radians(-angle))*mov_step

    if args[0] == b's':
        camx -= math.sin(math.radians(-angle))*mov_step
        camz -= math.cos(math.radians(-angle))*mov_step

def DrawBox(size):
    glBindTexture(GL_TEXTURE_2D, textureCube);
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

def DrawGLScene():
    global X_AXIS,Y_AXIS,Z_AXIS
    global DIRECTION
 
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
 
    glLoadIdentity()
    glTranslatef(0.0+camx,0.0,0.0+camz)
 
    glTranslatef(0.0-camx,0.0,0.0-camz)
    glRotatef(X_AXIS,1.0,0.0,0.0)
    glRotatef(Y_AXIS,0.0,1.0,0.0)
    glRotatef(Z_AXIS,0.0,0.0,1.0)
    glTranslatef(0.0+camx,0.0,-0.0+camz)
    #glBindTexture(GL_TEXTURE_2D, ID)
    #glBindTexture(GL_TEXTURE_2D, texture)   # 2d texture (x and y size)
    glPushMatrix();
    glTranslatef(-2.0,0.0,1.0)
    #glBindTexture(GL_TEXTURE_2D, image)
    
    for numz in range(0,10):
        for num in range(0,10):
            glBindTexture(GL_TEXTURE_2D, texture)   # 2d texture (x and y size)

            glBegin(GL_QUADS); # floor
            glTexCoord2f(1.0, 1.0); glVertex3f(-1.0 + num*2, -1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 1.0); glVertex3f( 1.0 + num*2, -1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 0.0); glVertex3f( 1.0 + num*2, -1.0,  1.0 - numz*2);
            glTexCoord2f(1.0, 0.0); glVertex3f(-1.0 + num*2, -1.0,  1.0 - numz*2);
            glEnd();

            glBegin(GL_QUADS); # roof
            glTexCoord2f(1.0, 1.0); glVertex3f(-1.0 + num*2, 1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 1.0); glVertex3f( 1.0 + num*2, 1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 0.0); glVertex3f( 1.0 + num*2, 1.0,  1.0 - numz*2);
            glTexCoord2f(1.0, 0.0); glVertex3f(-1.0 + num*2, 1.0,  1.0 - numz*2);
            glEnd();

            glBindTexture(GL_TEXTURE_2D, textureWall)   # 2d texture (x and y size)

            if matrix[num][numz] == 1:
                # Draw Cube (multiple quads)
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
    DrawBox(0.4);
    # X_AXIS = X_AXIS - 0.30
    # Z_AXIS = Z_AXIS - 0.30
    glutSwapBuffers()

def loadTexture (dirname, sfile, texture):
    l = lm.GetLod(dirname)
    ret = l.GetFileData("", sfile)
    
    width  = ret['img_size'][0]
    height = ret['img_size'][1]
    
    img = Image.new("P", ret['img_size'])
    img.putdata(ret['data'])
    img.putpalette(ret['palette'])
    img = img.convert("RGBX")
    image  = img.tostring ( "raw", "RGBX", 0, -1 )
    #texture = glGenTextures ( 1 )
    glBindTexture     ( GL_TEXTURE_2D, texture )   
    glPixelStorei     ( GL_UNPACK_ALIGNMENT,1 )
    glTexParameterf   ( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
    glTexParameterf   ( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
    glTexParameteri   ( GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR )
    glTexParameteri   ( GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_LINEAR )
    gluBuild2DMipmaps ( GL_TEXTURE_2D, 3, width, height, GL_RGBA, GL_UNSIGNED_BYTE, image )

    return texture

def main():
    global window
    global ID 
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(800,600)
    glutInitWindowPosition(200,200)

    window = glutCreateWindow(b'OpenGL Python Maze Test')

    global lm 
    lm = LodManager()
    lm.LoadLods('data')

    loadTexture ( "bitmaps", "bemob1b", texture )
    loadTexture ( "bitmaps", "bcsctr", textureWall )
    loadTexture ( "bitmaps", "cblrg", textureCube )
 
    glutDisplayFunc(DrawGLScene)
    glutIdleFunc(DrawGLScene)
    glutKeyboardFunc(keyPressed)
    InitGL(800, 600)

    glutMainLoop()
 
if __name__ == "__main__":
    main() 