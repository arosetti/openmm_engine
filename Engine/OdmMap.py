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
 char heightMap[MAP_SIZE*MAP_SIZE];
 char tileSetMap[MAP_SIZE*MAP_SIZE];
 char attributeMap[MAP_SIZE*MAP_SIZE];
 Shading shadingMap[MAP_SIZE*MAP_SIZE]; // two chars each /// Only exists in MM7 and MM8

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
 int idListAtCoordinateMap[MAP_SIZE*MAP_SIZE];

 int SpawnPointCount; // number of spawn points (monsters)
 SpawnPoint *spawnPoints;

};
'''

MAP_SIZE        =  128
MAP_PLAY_SIZE   =   88
MAP_TILE_SIZE   =  512
MAP_HEIGHT_SIZE =   32
MAP_OFFSET      =   64

MAP_HDR_SIZE    =  176
TILE_IDX_SIZE   =   16
TILE_HDR_SIZE   =    4

# make 3 dictionary with offsets and select the right one

HEIGHTMAP_OFFSET = MAP_HDR_SIZE
HEIGHTMAP_SIZE   = MAP_SIZE * MAP_SIZE

TILEMAP_OFFSET = MAP_HDR_SIZE + HEIGHTMAP_SIZE
TILEMAP_SIZE   = MAP_SIZE * MAP_SIZE

BMODELS_OFFSET = TILEMAP_OFFSET + TILEMAP_SIZE
BMODELS_HDR_SIZE = 0xBC

SPRITES_OFFSET = 0
SPRITES_HDR_SIZE   = 0x20

def get_filename(data):
    chunks = data.split(b'\x00')
    tmp = "{0}".format(chunks[0].decode('latin-1'))
    return tmp

class OdmMap(object):
    '''Map class'''
    def __init__(self, name, lm, tm):
        logging.config.fileConfig(os.path.join("conf", "log.conf"))
        self.log = logging.getLogger('LOD')
        self.lm = lm
        self.tm = tm

        self.mapdata = self.lm.GetLod("maps").GetFileData("", name)['data'] # TODO check error # remove from class when done
        self.log.info("Loading \"maps/{}\" {} bytes".format(name, len(self.mapdata)))
        s = struct.unpack_from('@32s32s32s32s32sHHHHHHHH', self.mapdata[:MAP_HDR_SIZE])

        if s[2].startswith(b'MM6 Outdoor v1.11'):
            self.version = 6
        elif s[2].startswith(b'MM6 Outdoor v7.00'):
            self.version = 7
        else:
            self.version = 8
        self.log.info("Map version {}".format(self.version))

        # heightmap
        self.heightmap = self.mapdata[HEIGHTMAP_OFFSET:HEIGHTMAP_OFFSET + HEIGHTMAP_SIZE]

        #tilemap
        self.tilemap = self.mapdata[TILEMAP_OFFSET:TILEMAP_OFFSET + TILEMAP_SIZE]

        '''
        #bmodels
        s = struct.unpack_from('@I', self.mapdata[BMODELS_OFFSET:BMODELS_OFFSET+4])
        self.nmodels = s[0]
        self.log.info("Map contains {} models".format(self.nmodels))
        self.model_hdr_size = BMODELS_HDR_SIZE * self.nmodels
        self.model_hdr = self.mapdata[SPRITES_OFFSET:SPRITES_OFFSET+4]
        
        #sprites
        SPRITES_OFFSET = 0x1019BC
        #s = struct.unpack_from('@I', self.mapdata[SPRITES_OFFSET:SPRITES_OFFSET+4])
        #self.nsprites = s[0]
        self.sprites = self.mapdata[SPRITES_OFFSET:SPRITES_OFFSET + 0x20 * self.nsprites]
        '''

        # TEXTURES
        self.log.info("Loading map textures".format(self.version))
        # sky
        self.sky_rot = 0.0
        self.tm.LoadTexture ("bitmaps", "sky07")
        #dtilebin
        self.dtilebin = self.lm.GetLod("icons").GetFileData("", "dtile.bin")['data'] # check error
        self.log.info("Loading \"icons/dtile.bin\" {} bytes".format(len(self.dtilebin)))

        self.LoadTileData()
        self.tex_name = "tex_atlas_a"
        tm.LoadAtlasTexture("tex_atlas_a", "bitmaps", self.imglist, (0,0xfc,0xfc), 'wtrtyl', 0 )
        tm.LoadAtlasTexture("tex_atlas_b", "bitmaps", self.imglist, (0,0xfc,0xfc), 'wtrtyl', 1 )

        self.LoadMapData()

        # THREADS
        twater = threading.Thread(target=self.threadWater) # TODO use shaders
        twater.daemon = True
        twater.start()

        t1 = threading.Thread(target=self.threadSky) # TODO do not use a cube.
        t1.daemon = True
        t1.start()

    def threadWater(self):
        while True:
            if self.tex_name == "tex_atlas_a":
                self.tex_name = "tex_atlas_b"
                time.sleep(.8)
            else:
                self.tex_name = "tex_atlas_a"
                time.sleep(.4)

    def threadSky(self):
        while True:
            time.sleep(.01)
            self.sky_rot = (self.sky_rot + 0.007) % 360.0

    def TerrainHeight(self, x, z):
        x = (x / MAP_TILE_SIZE) + MAP_OFFSET
        z = -(z / MAP_TILE_SIZE) + MAP_OFFSET
        return self.mesh[x][z][1]

    def LoadMapData(self):
        self.log.info("building mesh")
        self.mesh = numpy.empty((MAP_SIZE, MAP_SIZE, 3))
        for x in range(MAP_SIZE):
            for z in range(MAP_SIZE):
                self.mesh[x][z] = [MAP_TILE_SIZE * (x - MAP_OFFSET),
                                   MAP_HEIGHT_SIZE * (self.heightmap[x * MAP_SIZE + z]),
                                   -MAP_TILE_SIZE * (z - MAP_OFFSET)]
        self.log.info("building vertices")
        self.vertices = None
        self.textures = None
        self.colors = None
        s = (self.tm.textures["tex_atlas_a"]['hstep']) / (self.tm.textures["tex_atlas_a"]['h'])
        for z in range(0, MAP_SIZE - 1):
            for x in range(0, MAP_SIZE - 1):
                vertex = numpy.empty((6,3), dtype='float32')
                vertex[0] = [self.mesh[x][z][0], self.mesh[x][z][1], self.mesh[x][z][2]]
                vertex[1] = [self.mesh[x+1][z][0], self.mesh[x+1][z][1], self.mesh[x+1][z][2]]
                vertex[2] = [self.mesh[x][z+1][0], self.mesh[x][z+1][1], self.mesh[x][z+1][2]]
                vertex[3] = [self.mesh[x+1][z][0], self.mesh[x+1][z][1], self.mesh[x+1][z][2]]
                vertex[4] = [self.mesh[x][z+1][0], self.mesh[x][z+1][1], self.mesh[x][z+1][2]]
                vertex[5] = [self.mesh[x+1][z+1][0], self.mesh[x+1][z+1][1], self.mesh[x+1][z+1][2]]

                if self.vertices is not None:
                    self.vertices = numpy.concatenate([self.vertices, vertex])
                else:
                    self.vertices = vertex

                # why so slow in render ??!!
                #self.vertices.append([self.mesh[x][z][0], self.mesh[x][z][1], self.mesh[x][z][2]])
                #self.vertices.append([self.mesh[x+1][z][0], self.mesh[x+1][z][1], self.mesh[x+1][z][2]])
                #self.vertices.append([self.mesh[x][z+1][0], self.mesh[x][z+1][1], self.mesh[x][z+1][2]])
                #self.vertices.append([self.mesh[x+1][z][0], self.mesh[x+1][z][1], self.mesh[x+1][z][2]])
                #self.vertices.append([self.mesh[x][z+1][0], self.mesh[x][z+1][1], self.mesh[x][z+1][2]])
                #self.vertices.append([self.mesh[x+1][z+1][0], self.mesh[x+1][z+1][1], self.mesh[x+1][z+1][2]])

                tile_code = self.tilemap[x * MAP_SIZE + z]
                tile_name = self.GetTileName(tile_code)
                if tile_name is None:
                    tile_name = self.tex_names[tile_code]['name']
                try:
                    tile_index = self.imglist.index(tile_name)
                except:
                    tile_index = self.imglist.index('pending')

                if tile_name == 'pending':
                    print(tile_code)
                
                base = tile_index * s + (s / 128)
                top = base + s - 2 * (s / 128)

                texture = numpy.empty((6,2), dtype='float32')
                texture[0] = [0.0, base]
                texture[1] = [0.0, top]
                texture[2] = [1.0, base]
                texture[3] = [0.0, top]
                texture[4] = [1.0, base]
                texture[5] = [1.0, top]

                if self.textures is not None:
                    self.textures = numpy.concatenate([self.textures, texture])
                else:
                    self.textures = texture

                color = numpy.empty((1,3), dtype='float32')
                for v in vertex:
                    h = (v[1] / MAP_HEIGHT_SIZE)
                    if 0 <= h <= 5:
                        color[0] = [.625, .625, .625]
                    elif 6 <= h <= 14 :
                        color[0] = [.725, .725, .725]
                    elif 15 <= h <= 28:
                        color[0] = [.8, .8, .8]
                    elif 29 <= h <= 51:
                        color[0] = [.85, .85, .85]
                    elif 52 <= h >= 100:
                        color[0] = [.9, .9, .9]
                    else:
                        color[0] = [.95, .95, .95]

                    if self.colors is not None:
                        self.colors = numpy.concatenate([self.colors, color])
                    else:
                        self.colors = color

        self.log.info("map loaded")
        print(len(self.vertices))
        print(len(self.textures))
        print(len(self.colors))

        #self.vertices_gl = vbo.VBO(self.vertices) # TODO use vbos
        #self.colors_gl = vbo.VBO(self.colors)
        #self.textures_gl = vbo.VBO(self.textures)

    def GetTileType(self, c, base): # tile class
        group_type = ['ne', 'se', 'nw', 'sw', 'e', 'w', 'n', 's', 'xne', 'xse', 'xnw', 'xsw']
        offset = c - base
        if 0 <= offset < 12:
            return group_type[offset]
        return None
    
    def GetTileGroup(self, i):
        id1 = self.tileinfo['idx'][i]
        id2 = self.tileinfo['idx'][i+1]
        if  id1 == 1 and id2 == 342:
            return ['snotyl', 'snodr']
        if  id1 == 22 and id2 == 774:
            return ['wtrtyl', 'wtrdr']
        if  id1 == 0 and id2 == 90:
            return ['grastyl', 'grdrt']
        if  id1 == 2 and id2 == 234:
            return ['sandtyl', 'sndrt']
        if  id1 == 3 and id2 == 198:
            return ['voltyl', 'voldrt']
        if  id1 == 7 and id2 == 270:
            return ['swmtyl', 'swmdr']
        if  id1 == 8 and id2 == 306:
            return ['troptyl', 'trop']
        if  id1 == 6 and id2 == 162:
            return ['crktyl', 'crkdrt']
        else:
            return ['pending', 'pending']

    def GetTileName(self, c): # put odm idx as param, tile class
        if c >= 1 and c <=0x34:
            return 'dirttyl'
      
        t0_main, t0_prefix = self.GetTileGroup(0)  # TODO set in init
        t1_main, t1_prefix = self.GetTileGroup(2)
        t2_main, t2_prefix = self.GetTileGroup(4)
        t3_main, t3_prefix = self.GetTileGroup(6)

        if c >= 0x5a and c <= 0x65:
            return t0_main
        ret = self.GetTileType(c, 0x66)
        if ret is not None:
            return '{}{}'.format(t0_prefix,ret)

        #if c >= 0x7e and c <= 0x89: # road tyles
        #    return t1_main
        #ret = self.GetTileType(c, 0x8a)
        #if ret is not None:
        #    return '{}{}'.format(t1_prefix, ret)

        if c >= 0xa2 and c <= 0xad:
            return t2_main
        ret = self.GetTileType(c, 0xae)
        if ret is not None:
            return '{}{}'.format(t2_prefix, ret)

        if c >= 0x7e and c <= 0x89:
            return t3_main
        ret = self.GetTileType(c, 0x8a)
        if ret is not None:
            return '{}{}'.format(t3_prefix,ret)
        #self.log.debug("cant' finde texture code {}".format(c))
        return None

    def LoadTileData(self):
        s = struct.unpack_from('@I', self.dtilebin[:TILE_HDR_SIZE])
        self.dtilebin = self.dtilebin[TILE_HDR_SIZE:]
        s_idx = struct.unpack_from('@HHHHHHHH', self.mapdata[MAP_HDR_SIZE-TILE_IDX_SIZE:MAP_HDR_SIZE])
        self.tileinfo = { 'num': s[0],
                          'idx': s_idx }# 16 bytes
        print(self.tileinfo)
        self.tex_names = {}
        for i in range(256):  ### TODO merge with other implementation
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

        for x in ['wtrtyl','wtrdre','wtrdrn','wtrdrs','wtrdrw','wtrdrnw', 'wtrdrne','wtrdrsw','wtrdrse','wtrdrxne','wtrdrxnw','wtrdrxse','wtrdrxsw',
                  'voltyl','voldrte','voldrtn','voldrts','voldrtw','voldrtnw', 'voldrtne','voldrtsw','voldrtse','voldrtxne','voldrtxnw','voldrtxse','voldrtxsw',
                  'troptyl','trope','tropn','trops','tropw','tropnw', 'tropne','tropsw','tropse','tropxne','tropxnw','tropxse','tropxsw',
                  'snotyl','snodre','snodrn','snodrs','snodrw','snodrnw', 'snodrne','snodrsw','snodrse','snodrxne','snodrxnw','snodrxse','snodrxsw',
                  'sandtyl','sndrte','sndrtn','sndrts','sndrtw','sndrtnw', 'sndrtne','sndrtsw','sndrtse','sndrtxne','sndrtxnw','sndrtxse','sndrtxsw',
                  'swmtyl','swmdre','swmdrn','swmdrs','swmdrw','swmdrnw', 'swmdrne','swmdrsw','swmdrse','swmdrxne','swmdrxnw','swmdrxse','swmdrxsw',
                  'crktyl','crkdrte','crkdrtn','crkdrts','crkdrtw','crkdrtnw', 'crkdrtne','crkdrtsw','crkdrtse','crkdrtxne','crkdrtxnw','crkdrtxse','crkdrtxsw',
                  ]:
            if  x not in self.imglist:
                self.imglist += [x]

        print(len(self.imglist))
        self.imglist[:] = [x for x in self.imglist if self.lm.GetLod("bitmaps").FileExists(x)]
        #self.imglist.sort()
        print(self.imglist)
        print(len(self.imglist))

    def Draw(self):
        self.DrawSky()
        self.DrawTerrain()
        self.DrawGameArea()
        self.DrawAxis()

    def DrawTerrain(self):
        glBindTexture(GL_TEXTURE_2D, self.tm.textures[self.tex_name]['id'])
        glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glPushMatrix()

        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_VERTEX_ARRAY)

        glTexCoordPointer(2, GL_FLOAT, 0, self.textures)
        glColorPointer(3, GL_FLOAT, 0, self.colors)
        #glNormalPointer(3, GL_FLOAT, self.normals)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)

        #vertices_gl.bind()
        #colors_gl.bind()
        #glVertexPointer(2, GL_FLOAT, 0, self.vertices_gl)
        #glColorPointer(2, GL_FLOAT, 0, self.colors_gl)

        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices))

        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glEnable (GL_BLEND)
        glPopMatrix()

    def DrawGameArea(self):
        glPushMatrix();
        glDisable(GL_TEXTURE_2D)
        #glDisable(GL_DEPTH_TEST)
        glDisable (GL_BLEND)
        glLineWidth(2.0);
        glBegin(GL_LINES);
        glColor3f(1, 0, 0);
        glVertex3f(MAP_TILE_SIZE * MAP_PLAY_SIZE / 2, 512, MAP_TILE_SIZE * MAP_PLAY_SIZE / 2);
        glVertex3f(MAP_TILE_SIZE * MAP_PLAY_SIZE / 2, 512, -MAP_TILE_SIZE * MAP_PLAY_SIZE / 2);
        glColor3f(0, 1, 0);
        glVertex3f(MAP_TILE_SIZE * MAP_PLAY_SIZE / 2, 512, MAP_TILE_SIZE * MAP_PLAY_SIZE / 2);
        glVertex3f(-MAP_TILE_SIZE * MAP_PLAY_SIZE / 2, 512, MAP_TILE_SIZE * MAP_PLAY_SIZE / 2);
        glColor3f(0, 0, 1);
        glVertex3f(-MAP_TILE_SIZE * MAP_PLAY_SIZE / 2, 512, MAP_TILE_SIZE * MAP_PLAY_SIZE / 2);
        glVertex3f(-MAP_TILE_SIZE * MAP_PLAY_SIZE / 2, 512, -MAP_TILE_SIZE * MAP_PLAY_SIZE / 2);
        glColor3f(1, 1, 0);
        glVertex3f(-MAP_TILE_SIZE * MAP_PLAY_SIZE / 2, 512, -MAP_TILE_SIZE * MAP_PLAY_SIZE / 2);
        glVertex3f(MAP_TILE_SIZE * MAP_PLAY_SIZE / 2, 512, -MAP_TILE_SIZE * MAP_PLAY_SIZE / 2);
        glEnd();
        glEnable(GL_TEXTURE_2D)
        #glEnable(GL_DEPTH_TEST)
        glEnable (GL_BLEND)
        glPopMatrix();

    def DrawSky(self):
        glBindTexture(GL_TEXTURE_2D, self.tm.textures["sky07"]['id']) # TODO load texture in costructor.
        glPushMatrix();
        glScaled(60000,60000,60000);
        glRotatef(self.sky_rot, 0.0, 1.0, 0.0);
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

    def DrawAxis(self):
        l=512
        l2=512+50
        glPushMatrix();
        #glDisable(GL_COLOR_MATERIAL)
        #glDisable(GL_LIGHTING)
        #glDisable(GL_BLEND)
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
        # WARNING this causes a segfault on exit
        #glColor3f(1.0, 1.0, 0.2)
        #glRasterPos3f(l2, 0.0, 0.0)
        #glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord('x'))
        #glRasterPos3f(0.0, l2, 0.0)
        #glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord('y'))
        #glRasterPos3f(0.0, 0.0, l2)
        #glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord('z'))
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix();
