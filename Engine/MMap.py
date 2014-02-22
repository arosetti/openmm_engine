import sys, array, struct, math, numpy

from Lod import *
from Engine import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from PIL import Image
import threading, time
import logging, logging.config
import pprint
from decimal import Decimal

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
  int unknown;                 /// Only exists in MM7 and MM8
  int unknown;                 /// Only exists in MM7 and MM8

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
HDR_MAP  =  176
TILE_IDX =   16
DTILE    =    4

MAP_SIZE = 128
MAP_PLAYABLE_SIZE = 88

def get_filename(data):
    chunks = data.split(b'\x00')
    tmp = "{0}".format(chunks[0].decode('latin-1'))
    return tmp

class MMap(object):
    '''Map class'''

    def __init__(self, name, lm, tm):
        logging.config.fileConfig(os.path.join("conf", "log.conf"))
        self.log = logging.getLogger('LOD')
        self.lm = lm
        self.tm = tm

        self.ts = 512
        self.hs = 32
        self.off = 64

        self.mapdata = self.lm.GetLod("maps").GetFileData("", name)['data'] # check error
        self.log.info("Loading \"maps/{}\" {} bytes".format(name, len(self.mapdata)))
        s = struct.unpack_from('@32s32s32s32s32sHHHHHHHH', self.mapdata[:HDR_MAP])
        #print(s)
        #TODO detect version 6,7,8

        # heightmap
        self.heightmap = self.mapdata[HDR_MAP:HDR_MAP+128*128]
        #img = Image.new("P", (128,128))
        #img.putdata(self.heightmap)
        #img.save("tmp/{}_height.bmp".format(name))
        #f = open("tmp/{}_height.dat".format(name), "wb")
        #f.write(self.heightmap)
        #f.close()

        #tilemap
        self.tilemap = self.mapdata[HDR_MAP+128*128:HDR_MAP+2*128*128]
        #img = Image.new("P", (128,128))
        #img.putdata(self.tilemap)
        #img.save("tmp/{}_tile.bmp".format(name))
        #f = open("tmp/{}_tile.dat".format(name), "wb")
        #f.write(self.tilemap)
        #f.close()

        #dtilebin
        self.dtilebin = self.lm.GetLod("icons").GetFileData("", "dtile.bin")['data'] # check error
        self.log.info("Loading \"icons/dtile.bin\" {} bytes".format(len(self.dtilebin)))


        self.LoadTileData()
        self.tex_name = "tex_atlas_a"
        tm.LoadAtlasTexture("tex_atlas_a", "bitmaps", self.imglist, (0,0xfc,0xfc), 'wtrtyl', 0 )
        tm.LoadAtlasTexture("tex_atlas_b", "bitmaps", self.imglist, (0,0xfc,0xfc), 'wtrtyl', 1 )
        self.LoadMapData(name)

        twater = threading.Thread(target=self.threadWater)
        twater.daemon = True
        twater.start()

    def threadWater(self):
        while True:
            if self.tex_name == "tex_atlas_a":
                self.tex_name = "tex_atlas_b"
                time.sleep(.8)
            else:
                self.tex_name = "tex_atlas_a"
                time.sleep(.4)

    def TerrainHeight(self, x, z):
        x = int(x / self.ts + self.off)
        z = int(z / self.ts - self.off)
        return self.mesh[x][z][1]

    def LoadMapData(self,name):
        self.log.info("building mesh")
        self.mesh = numpy.empty((128,128,3))
        for x in range(128):
            for z in range(128):
                self.mesh[x][z] = [self.ts*(x-self.off),self.hs*(self.heightmap[x*128+z]),-self.ts*(z-self.off)]
        self.log.info("building vertexes")
        self.vertexes = None
        self.textures = None
        #print(self.tm.textures["tex_atlas_a"]['h'] / self.tm.textures["tex_atlas_a"]['hstep'])
        s = Decimal(self.tm.textures["tex_atlas_a"]['hstep']) / Decimal(self.tm.textures["tex_atlas_a"]['h'])
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

                tile_name = self.GetTileName(x, z)
                if tile_name is None:
                    tile_type = self.tilemap[x*128+z]
                    tile_name = self.tex_names[tile_type]['name']
                try:
                    tile_index = self.imglist.index(tile_name)
                except:
                    tile_index = self.imglist.index('pending')

                if tile_name == 'pending':
                    print(tile_type)
                
                base = Decimal(tile_index)*s
                top = base + s

                texture = numpy.empty((6,2), dtype='float64')
                texture[0] = [0.0,base]
                texture[1] = [0.0, top]
                texture[2] = [1.0,base]
                texture[3] = [0.0, top]
                texture[4] = [1.0,base]
                texture[5] = [1.0, top]

                if self.textures is not None:
                    self.textures = numpy.concatenate([self.textures, texture])
                else:
                    self.textures = texture
        self.log.info("map loaded")

    def GetTileType(self, c, base): # tile class
        group_type = ['ne', 'se', 'nw', 'sw', 'e', 'w', 'n', 's', 'xne', 'xse', 'xnw', 'xsw']
        offset = c - base
        if 0 <= offset < 12:
            return group_type[offset]
        return None

    def GetTileName(self, x, z): # put odm idx as param, tile class
        c = self.tilemap[x*128+z]
        if c >= 1 and c <=0x34:
            return 'dirttyl'

        if c >= 0x5a and c <=0x65: #grass
            return 'grastyl'
        ret = self.GetTileType(c, 0x66)
        if ret is not None:
            return 'grdrt{}'.format(ret)

        if c >= 0x7e and c <= 0x89: #water
            return 'wtrtyl'
        ret = self.GetTileType(c, 0x8a)
        if ret is not None:
            return 'wtrdr{}'.format(ret)

        if c >= 0xa2 and c <= 0xad: #other ...
            return 'voltyl'
        ret = self.GetTileType(c, 0xae)
        if ret is not None:
            return 'voldrt{}'.format(ret)

        #self.log.debug("cant' finde texture code {}".format(c))
        return None

    def LoadTileData(self):
        s = struct.unpack_from('@I', self.dtilebin[:DTILE])
        self.tileinfo = { 'num': s[0],
                          'idx': self.mapdata[HDR_MAP-TILE_IDX:HDR_MAP] }# 16 bytes
        print(self.tileinfo)
        self.dtilebin = self.dtilebin[DTILE:]
        self.tex_names = {}
        s_idx = struct.unpack_from('@HHHHHHHH', self.tileinfo['idx'])
        print(s_idx)
        for i in range(256):  ### this is a mess
             index = 0
             if i >= 0xc6: # roads
                 index = i - 0xc6 + s_idx[7]
             else:
                 if i < 0x5a: # grass-dirt ?
                     index = i
                 else:  # borders
                     n = int((i - 0x5a) / 0x24)
                     index = s_idx[n] - n * 0x24
                     index += i - 0x5a
             s_tbl = struct.unpack_from('=20sHHH', self.dtilebin[index*0x1a:(index+1)*0x1a])
             if s_tbl[0][0] == 0:
                 self.tex_names[i] = {'name': 'pending', 'name2': ''}
             else:
                 self.tex_names[i] = {'name': get_filename(s_tbl[0]).lower(), 'name2': ''}

        self.imglist = []
        for i in self.tex_names:
            if self.tex_names[i]['name'] not in self.imglist:
                self.imglist += [self.tex_names[i]['name']]

        for x in ['wtrtyl','wtrdre','wtrdrn','wtrdrne','wtrdrnw','wtrdrs', 'wtrdrse','wtrdrsw','wtrdrw','wtrdrxne','wtrdrxnw','wtrdrxse','wtrdrxsw',
                  'voltyl','voldrte','voldrtn','voldrtne','voldrtnw','voldrts', 'voldrtse','voldrtsw','voldrtw','voldrtxne','voldrtxnw','voldrtxse','voldrtxsw']:
            if  x not in self.imglist:
                self.imglist += [x]

        print(len(self.imglist))
        self.imglist[:] = [x for x in self.imglist if self.lm.GetLod("bitmaps").FileExists(x)]
        #self.imglist.sort()
        print(self.imglist)
        print(len(self.imglist))

    def Draw(self):
        glBindTexture(GL_TEXTURE_2D, self.tm.textures[self.tex_name]['id'])
        glPushMatrix()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer (3, GL_FLOAT, 0, self.vertexes)
        glEnableClientState (GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_DOUBLE, 0, self.textures)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertexes))
        glDisableClientState (GL_VERTEX_ARRAY)
        glDisableClientState (GL_TEXTURE_COORD_ARRAY)
        glPopMatrix()

    def DrawGameArea(self):
        glPushMatrix();
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glLineWidth(1.0);
        glBegin(GL_LINES);
        glColor3f(1,0,0);
        glVertex3f(512*44, 64, 512*44);
        glVertex3f(512*44, 64, -512*44);
        glColor3f(0,1,0);
        glVertex3f(512*44, 64, 512*44);
        glVertex3f(-512*44, 64, 512*44);
        glColor3f(0,0,1);
        glVertex3f(-512*44, 64, 512*44);
        glVertex3f(-512*44, 64, -512*44);
        glColor3f(1,1,0);
        glVertex3f(-512*44, 64, -512*44);
        glVertex3f(512*44, 64, -512*44);
        glEnd();
        glEnable(GL_TEXTURE_2D)
        glPopMatrix();
