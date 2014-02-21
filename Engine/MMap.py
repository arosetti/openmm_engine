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
        tm.LoadAtlasTexture("tiles_megatexture", "bitmaps", self.imglist )
        self.LoadMapData(name)

    def LoadMapData(self,name):

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
        print(self.tm.textures["tiles_megatexture"]['h'] / self.tm.textures["tiles_megatexture"]['hstep'])
        print(self.tm.textures["tiles_megatexture"]['h'])
        print(self.tm.textures["tiles_megatexture"]['hstep'] )
        s = Decimal(self.tm.textures["tiles_megatexture"]['hstep']) / Decimal(self.tm.textures["tiles_megatexture"]['h'])
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
                    #if self.tex_names[x]['name2'] != '':
                    #    tile_name = self.tex_names[x]['name2']
                try:
                    tile_index = self.imglist.index(tile_name)
                except:
                    tile_index = self.imglist.index('pending')
                texture = numpy.empty((6,2), dtype='float64')

                if tile_name == 'pending':
                    print(tile_type)
                
                base = Decimal(tile_index)*s
                top = Decimal(tile_index+1)*s

                #print("{} {}".format(base,top))

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

    def GetTileName(self, x, z):
        c = self.tilemap[x*128+z]
        if c >= 1 and c <=52:
            return 'dirttyl'
        #grass
        if c >= 0x5a and c <=0x65:
            return 'grastyl'
        if c == 0x66:
            return 'grdrtne'
        if c == 0x67:
            return 'grdrtse'
        if c == 0x68:
            return 'grdrtnw'
        if c == 0x69:
            return 'grdrtsw'
        if c == 0x6a:
            return 'grdrte'
        if c == 0x6b:
            return 'grdrtw'
        if c == 0x6c:
            return 'grdrtn'
        if c == 0x6d:
            return 'grdrts'
        if c == 0x6e:
            return 'grdrtxne'
        if c == 0x6f:
            return 'grdrtxse'
        if c == 0x70:
            return 'grdrtxnw'
        if c == 0x71:
            return 'grdrtxsw'
        #water
        if c >= 0x7e and c <= 0x89:
            return 'wtrtyl'
        if c == 0x8a:
            return 'wtrdrne'
        if c == 0x8b:
            return 'wtrdrse'
        if c == 0x8c:
            return 'wtrdrnw'
        if c == 0x8d:
            return 'wtrdrsw'
        if c == 0x8e:
            return 'wtrdre'
        if c == 0x8f:
            return 'wtrdrw'
        if c == 0x90:
            return 'wtrdrn'
        if c == 0x91:
            return 'wtrdrs'
        if c == 0x92:
            return 'wtrdrxne'
        if c == 0x93:
            return 'wtrdrxse'
        if c == 0x94:
            return 'wtrdrxnw'
        if c == 0x95:
            return 'wtrdrxsw'


        #vulcaic
        if c >= 0xa2 and c <= 0xad:
            return 'voltyl'
        if c == 0xae:
            return 'voldrtne'
        if c == 0xaf:
            return 'voldrtse'
        if c == 0xb0:
            return 'voldrtnw'
        if c == 0xb1:
            return 'voldrtsw'
        if c == 0xb2:
            return 'voldrte'
        if c == 0xb3:
            return 'voldrtw'
        if c == 0xb4:
            return 'voldrtn'
        if c == 0xb5:
            return 'voldrts'
        if c == 0xb6:
            return 'voldrtxne'
        if c == 0xb7:
            return 'voldrtxse'
        if c == 0xb8:
            return 'voldrtxnw'
        if c == 0xb9:
            return 'voldrtxsw'
        #print("cant' finde code {}".format(c))
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
             #print ("name1 {}: {}".format(index, self.tex_names[i]['name']))
             #if s_tbl[3] == 512:
             #    for j in range(0,8,2):
             #        if s_idx[j] == s_tbl[1]:
             #            s_tbl2 = struct.unpack_from('=20sHHH', self.dtilebin[s_idx[j+1]*0x1a:(s_idx[j+1]+1)*0x1a])
             #            if s_tbl2[0][0] == 0:
             #                self.tex_names[i].update({'name2': 'pending'})
             #            else:
             #                self.tex_names[i].update({'name2': get_filename(s_tbl2[0]).lower()})
             #            print ("name2 {}: {}".format(index, self.tex_names[i]['name2']))
             #            break
        self.imglist = []
        for i in self.tex_names:
            if self.tex_names[i]['name'] not in self.imglist:
                self.imglist += [self.tex_names[i]['name']]
            #name = self.tex_names[x]['name2']
            #if  name != '' and name not in self.imglist:
            #    self.imglist.append(name)

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
        glBindTexture(GL_TEXTURE_2D, self.tm.textures["tiles_megatexture"]['id'])
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
