#!/usr/bin/env python3

'''
this script has been taken from http://openglsamples.sourceforge.net/
modified to work with python3
it's an interesting example of use of openg with python
'''

import io, sys, math, numpy
from Lod import *
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

lm = 0
window = 0
ID = 0

#rotation
X_AXIS = 0.0
Y_AXIS = 0.0
Z_AXIS = 0.0



DIRECTION = 1

textureFloor  = 0
textureCeil  = 1
textureWall = 2
textureCube = 3
textureSky = 4
textureBorder1 = 5
textureBorder2 = 6
textureBorder3 = 7
textureBorder4 = 8
textureEradcate = 9
textureMaleA01 = 10
textureTap2 = 11
textureFooter = 12

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
    #glDepthFunc(GL_LESS)
    glDepthFunc(GL_LEQUAL) 
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)   
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50.0, float(Width)/float(Height), 0.1, 300.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_TEXTURE_2D) # initialize texture mapping

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable (GL_BLEND)
    glDisable(GL_COLOR_MATERIAL)

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

def DrawBox():
    glBindTexture(GL_TEXTURE_2D, textureCube);
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
    glBindTexture(GL_TEXTURE_2D, textureSky);
    glScaled(200,200,200);
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
    glTranslatef(-2.0,0.0,1.0)
    for numz in range(0,10):
        for num in range(0,10):
            glBindTexture(GL_TEXTURE_2D, textureFloor)   # 2d texture (x and y size)
            glBegin(GL_QUADS); # floor
            glTexCoord2f(1.0, 1.0); glVertex3f(-1.0 + num*2, -1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 1.0); glVertex3f( 1.0 + num*2, -1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 0.0); glVertex3f( 1.0 + num*2, -1.0,  1.0 - numz*2);
            glTexCoord2f(1.0, 0.0); glVertex3f(-1.0 + num*2, -1.0,  1.0 - numz*2);
            glEnd();

            glBindTexture(GL_TEXTURE_2D, textureCeil)
            glBegin(GL_QUADS); # roof
            glTexCoord2f(1.0, 1.0); glVertex3f(-1.0 + num*2, 1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 1.0); glVertex3f( 1.0 + num*2, 1.0, -1.0 - numz*2);
            glTexCoord2f(0.0, 0.0); glVertex3f( 1.0 + num*2, 1.0,  1.0 - numz*2);
            glTexCoord2f(1.0, 0.0); glVertex3f(-1.0 + num*2, 1.0,  1.0 - numz*2);
            glEnd();

            glBindTexture(GL_TEXTURE_2D, textureWall)   # 2d texture (x and y size)
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

def Set2DMode():
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    #gluOrtho2D(0.0, 640, 0.0, 480);
    glOrtho(0, 640, 480, 0, -1, 1);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glDisable(GL_DEPTH_TEST)

def Draw2DImage(texture, w, h, x, y):
    glBindTexture(GL_TEXTURE_2D, texture)
    glPushMatrix();
    glTranslatef(x,y,0);
    glBegin(GL_QUADS);
    glTexCoord2f(0.0, 1.0); glVertex2f(0.0, 0.0); 
    glTexCoord2f(0.0, 0.0); glVertex2f(0.0, h);
    glTexCoord2f(1.0, 0.0); glVertex2f(w, h);
    glTexCoord2f(1.0, 1.0); glVertex2f(w, 0.0); 
    glEnd();
    glPopMatrix();

def Set3DMode():
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(50.0, 640.0 / 480.0, 1, 300);
    #gluLookAt(0, 0, 400, 0, 0, 0, 0.0, 1.0, 0.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glEnable(GL_TEXTURE_2D) # initialize texture mapping
    glEnable(GL_LIGHTING);

def DrawGLScene():
    global X_AXIS,Y_AXIS,Z_AXIS
    global DIRECTION
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    Set3DMode()

    glTranslatef(0.0+camx,0.0,0.0+camz)
    glTranslatef(0.0-camx,0.0,0.0-camz)
    glRotatef(X_AXIS,1.0,0.0,0.0)
    glRotatef(Y_AXIS,0.0,1.0,0.0)
    glRotatef(Z_AXIS,0.0,0.0,1.0)
    glTranslatef(0.0+camx,0.0,-0.0+camz)

    DrawDungeon()
    DrawBox()
    DrawSky()

    Set2DMode()

    Draw2DImage(textureBorder1,  172.0,339.0, 640-172.0,480-339.0)
    Draw2DImage(textureFooter,   483.0,24.0,  0.0,480-109-24+2)
    Draw2DImage(textureBorder2,  469.0,109.0, 0.0,480-109.0)
    Draw2DImage(textureBorder3,  468.0,8.0,   0.0,0.0)
    Draw2DImage(textureBorder4,  8.0,344.0,   0.0,0.0)
    Draw2DImage(textureMaleA01,  59.0,79.0,   23.0,383.0)
    Draw2DImage(textureEradcate, 59.0,79.0,   136.0,383.0) # distance ~113px
    Draw2DImage(textureTap2,     172.0,142.0, 640-172.0,0.0)

    glEnable(GL_DEPTH_TEST);
    glutSwapBuffers();

def loadTexture (dirname, sfile, texture, transparency_color=None):
    l = lm.GetLod(dirname)
    ret = l.GetFileData("", sfile)
    width  = 0
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
    img = img.convert("RGBX")
    
    if transparency_color is not None:
        t=transparency_color
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if set(img.getpixel((x, y))) == set((t[0], t[1], t[2], 255)):
                    img.putpixel((x, y), (t[0], t[1], t[2], 0))
    
    image  = img.tostring("raw", "RGBX", 0, -1)
            
    #texture = glGenTextures ( 1 )
    glBindTexture     ( GL_TEXTURE_2D, texture )   
    glPixelStorei     ( GL_UNPACK_ALIGNMENT,1 )
    glTexParameterf   ( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
    glTexParameterf   ( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
    glTexParameteri   ( GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR ) #NEAREST
    glTexParameteri   ( GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST_MIPMAP_LINEAR ) #any combo
    gluBuild2DMipmaps ( GL_TEXTURE_2D, 3, width, height, GL_RGBA, GL_UNSIGNED_BYTE, image )

    return texture

def main():
    global window
    global ID 
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(640,480)
    glutInitWindowPosition(200,200)

    window = glutCreateWindow(b'Openmm_engine test')

    global lm 
    lm = LodManager()
    lm.LoadLods('data')

    loadTexture ("bitmaps", "bemob2b", textureFloor)
    loadTexture ("bitmaps", "d2ceil4", textureCeil)
    loadTexture ("bitmaps", "bcsctr", textureWall)
    loadTexture ("bitmaps", "cbsm", textureCube)
    loadTexture ("bitmaps", "sky07", textureSky)

    loadTexture ("icons", "border1.pcx", textureBorder1)
    loadTexture ("icons", "border2.pcx", textureBorder2)
    loadTexture ("icons", "border3", textureBorder3)
    loadTexture ("icons", "border4", textureBorder4)
    loadTexture ("icons", "eradcate", textureEradcate)
    loadTexture ("icons", "malea01", textureMaleA01)
    loadTexture ("icons", "tap2", textureTap2, (255,0,0))
    loadTexture ("icons", "footer", textureFooter)
    
    glutDisplayFunc(DrawGLScene)
    glutIdleFunc(DrawGLScene)
    glutKeyboardFunc(keyPressed)
    InitGL(640, 480)

    t = threading.Thread(target=threadInc)
    t.daemon = True
    t.start()

    glutMainLoop()
 
if __name__ == "__main__":
    main() 
