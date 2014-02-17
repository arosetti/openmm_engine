import sys, array, struct, math, numpy

from Lod import *
from Engine import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

import logging, logging.config
import pprint

HDR_MAP =  176

'''
struct ODM
{
 // header
 unsigned char  blank[32];  // map name -- normally left blank /// Probably not used by Engine
 unsigned char  defaultOdm[32];        // byte[32] @ 000020 // filename of map -- normally "default.odm" /// Probably not used by Engine
 unsigned char  editor[32]; // byte[32] @ 000040 // editor version string /// Probably not used by Engine  // in mm8, 31 bytes, master tile is last byte
 unsigned char  sky_texture[32];   /// Probably not used by Engine
 unsigned char  ground_texture[32];  /// Probably not used by Engine
 TilesetSelector tileset_selector[3]; 
 TilesetSelector road_tileset; TODO: section on tileset selector.   short group, id. See BDJ tutorial.
 int attributes; /// Only exists in MM8

 // coordinate maps
 char heightMap[128*128];
 char tileSetMap[128*128];
 char attributeMap[128*128];
 Shading shadingMap[128*128]; // two chars each /// Only exists in MM7 and MM8

  short width;            // width /// Only exists in MM7 and MM8
  short height;           // height /// Only exists in MM7 and MM8
  short width2;           // width /// Only exists in MM7 and MM8
  short height2;          // height /// Only exists in MM7 and MM8
  int unknown; 				/// Only exists in MM7 and MM8
  int unknown;     			/// Only exists in MM7 and MM8

 int bModelCount; // number of 3d model data sets
 BModel *bmodels;

 int SpriteCount; // number of billboard objects, 2d images in 3d space
 Sprite *sprites;
 
 // Sprite location id list and location by tile map
 int idDataCount; // number of idDataEntries in the list
 short idDataList[idDataCount];
 int idListAtCoordinateMap[128*128];

 int SpawnPointCount; // number of spawn points (monsters)
 SpawnPoint *spawnPoints;

};
'''

class MMap(object):
    '''Single lod archive class'''

    def __init__(self, name):
        logging.config.fileConfig('conf/log.conf')
        self.log = logging.getLogger('LOD')
        self.lm = LodManager()    
        self.lm.LoadLods('data')
        self.mapdata = self.lm.GetLod("maps").GetFileData("", name)['data'] # check error
        self.log.info("Loading \"maps/{}\" {} bytes".format(name, len(self.mapdata)))
        s = struct.unpack_from('@32s32s32s32s32sHHHHHHHH', self.mapdata[:HDR_MAP])
        print(s)

        self.heightmap = self.mapdata[HDR_MAP:HDR_MAP+128*128]
        img = Image.new("P", (128,128))
        img.putdata(self.heightmap)
        img.save("{}.bmp".format(name))

        f = open("{}.dat".format(name), "wb")
        f.write(self.heightmap)

        self.mesh = numpy.zeros((128,128,3))
        for x in range(128):
            for z in range(128):
                height = 0.2 * self.heightmap[x*128+z]
                self.mesh[x][z] = [float(x),float(height),float(z)]

        self.vertexes = None
        self.textures = None
        for z in range(127):
            for x in range(127):
                vertex = numpy.zeros((6,3))
                #triangle_strip
                #vertex[0] = [self.mesh[x][z][0], self.mesh[x][z][1], self.mesh[x][z][2]]
                #vertex[1] = [self.mesh[x+1][z][0], self.mesh[x+1][z][1], self.mesh[x+1][z][2]]
                #vertex[2] = [self.mesh[x][z+1][0], self.mesh[x][z+1][1], self.mesh[x][z+1][2]]
                #vertex[3] = [self.mesh[x+1][z+1][0], self.mesh[x+1][z+1][1], self.mesh[x+1][z+1][2]]
                vertex[0] = [self.mesh[x][z][0] , self.mesh[x][z][1], self.mesh[x][z][2]]
                vertex[1] = [self.mesh[x+1][z][0], self.mesh[x+1][z][1], self.mesh[x+1][z][2]]
                vertex[2] = [self.mesh[x][z+1][0], self.mesh[x][z+1][1], self.mesh[x][z+1][2]]
                vertex[3] = [self.mesh[x][z][0], self.mesh[x][z][1], self.mesh[x][z][2]]
                vertex[4] = [self.mesh[x][z+1][0], self.mesh[x][z+1][1], self.mesh[x][z+1][2]]
                vertex[5] = [self.mesh[x+1][z+1][0], self.mesh[x+1][z+1][1], self.mesh[x+1][z+1][2]]

                if self.vertexes is not None:
                    self.vertexes = numpy.concatenate([self.vertexes, vertex])
                else:
                    self.vertexes = vertex

                texture = numpy.zeros((6,2))
                #texture[0] = [0.0,0.0]
                #texture[1] = [1.0,0.0]
                #texture[2] = [0.0,1.0]
                #texture[3] = [1.0,1.0]
                texture[0] = [0.0,0.0]
                texture[1] = [1.0,0.0]
                texture[2] = [0.0,1.0]
                texture[3] = [0.0,0.0]
                texture[4] = [0.0,1.0]
                texture[5] = [1.0,1.0]

                if self.textures is not None:
                    self.textures = numpy.concatenate([self.textures, texture])
                else:
                    self.textures = texture

    def Draw(self, px, pz):
        '''
        # this works but it's slow
        q = 70
        minx = px - q/2
        if minx < 0:
            minx = 0
        maxx = px + q/2
        if minx > 127:
            maxx = 127

        minz = pz - q/2
        if minz < 0:
            minz = 0
        maxz = pz + q/2
        if minz > 127:
            maxz = 127

        for z in range(int(minz),int(maxz)):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range(int(minx),int(maxx)):
                glTexCoord2f(0.0, 0.0);
                glvertexes3f(self.mesh[x][z][0], 
                           self.mesh[x][z][1], self.mesh[x][z][2]);

                glTexCoord2f(1.0, 0.0);
                glvertexes3f(self.mesh[x+1][z][0], self.mesh[x+1][z][1], 
                           self.mesh[x+1][z][2]);

                glTexCoord2f(0.0, 1.0);
                glvertexes3f(self.mesh[x][z+1][0], self.mesh[x][z+1][1], 
                           self.mesh[x][z+1][2]);

                glTexCoord2f(1.0, 1.0);
                glvertexes3f(self.mesh[x+1][z+1][0], 
                           self.mesh[x+1][z+1][1], 
                           self.mesh[x+1][z+1][2]);
            glEnd();
        '''

        #glBindTexture(GL_TEXTURE_2D, tex);
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState (GL_TEXTURE_COORD_ARRAY)
        glVertexPointer (3, GL_FLOAT, 0, self.vertexes)
        glTexCoordPointer(2, GL_FLOAT, 0, self.textures);
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertexes))

