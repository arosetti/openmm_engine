import sys, array, struct, math, numpy

from Lod import *
from Engine import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
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

    def __init__(self, name, lm):
        logging.config.fileConfig('conf/log.conf')
        self.log = logging.getLogger('LOD')
        self.lm = lm
        
        self.tiledata = self.lm.GetLod("icons").GetFileData("", "dtile.bin")['data'] # check error
        self.log.info("Loading \"icons/dtile.bin\" {} bytes".format(name, len(self.tiledata)))
        #s = struct.unpack_from('@', self.mapdata[:HDR_MAP])

        self.mapdata = self.lm.GetLod("maps").GetFileData("", name)['data'] # check error
        self.log.info("Loading \"maps/{}\" {} bytes".format(name, len(self.mapdata)))
        s = struct.unpack_from('@32s32s32s32s32sHHHHHHHH', self.mapdata[:HDR_MAP])
        #print(s)

        self.heightmap = self.mapdata[HDR_MAP:HDR_MAP+128*128]
        img = Image.new("P", (128,128))
        img.putdata(self.heightmap)
        img.save("tmp/{}_height.bmp".format(name))

        f = open("tmp/{}_height.dat".format(name), "wb")
        f.write(self.heightmap)
        f.close()
        
        self.tilesetmap = self.mapdata[HDR_MAP+128*128:HDR_MAP+2*128*128]
        img = Image.new("P", (128,128))
        img.putdata(self.tilesetmap)
        img.save("tmp/{}_tile.bmp".format(name))

        f = open("tmp/{}_tile.dat".format(name), "wb")
        f.write(self.tilesetmap)
        f.close()

        ts = 512
        hs = 32
        off = 64
        self.log.info("building mesh")
        self.mesh = numpy.empty((128,128,3))
        for x in range(128):
            for z in range(128):
                height = self.heightmap[x*128+z]
                self.mesh[x][z] = [ts*float(x-off),hs*float(height),-ts*float(z-off)]
        self.log.info("building vertexes")
        self.vertexes = None
        self.textures = None
        for z in range(0,127):
            for x in range(0,127):
                vertex = numpy.empty((6,3), dtype='float32')
                vertex[0] = [self.mesh[x][z][0], self.mesh[x][z][1], self.mesh[x][z][2]]
                vertex[1] = [self.mesh[x+1][z][0], self.mesh[x+1][z][1], self.mesh[x+1][z][2]]
                vertex[2] = [self.mesh[x][z+1][0], self.mesh[x][z+1][1], self.mesh[x][z+1][2]]
                vertex[3] = [self.mesh[x+1][z][0], self.mesh[x+1][z][1], self.mesh[x+1][z][2]]
                vertex[4] = [self.mesh[x][z+1][0], self.mesh[x][z+1][1], self.mesh[x][z+1][2]]
                vertex[5] = [self.mesh[x+1][z+1][0], self.mesh[x+1][z+1][1], self.mesh[x+1][z+1][2]]

                if self.vertexes is not None:
                    self.vertexes = numpy.concatenate([self.vertexes, vertex])
                else:
                    self.vertexes = vertex

                texture = numpy.empty((6,2), dtype='float32')
                texture[0] = [0.0,0.0]
                texture[1] = [1.0,0.0]
                texture[2] = [0.0,1.0]
                texture[3] = [1.0,0.0]
                texture[4] = [0.0,1.0]
                texture[5] = [1.0,1.0]

                if self.textures is not None:
                    self.textures = numpy.concatenate([self.textures, texture])
                else:
                    self.textures = texture
        self.log.info("map loaded")

    def Draw(self):
        #glBindTexture(GL_TEXTURE_2D, tex);
        glPushMatrix()
        #glEnableClientState(GL_INDEX_ARRAY) 
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer (3, GL_FLOAT, 0, self.vertexes)
        glEnableClientState (GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_FLOAT, 0, self.textures)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertexes))
        glDisableClientState (GL_VERTEX_ARRAY)
        glDisableClientState (GL_TEXTURE_COORD_ARRAY)
        glPopMatrix()
