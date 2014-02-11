import sys, os, array, struct
import logging, logging.config
import zlib, pprint
from PIL import Image

def get_img(data, h, w):
    img = Image.frombytes("P", (h, w), data, "raw", "P", 0, 1)
    return img.getdata()

def get_filename(data):
    chunks = data.split(b'\x00')
    tmp = "{0}".format(chunks[0].decode('latin-1'))
    return tmp

def get_full_filename(data):
    chunks = data.split(b'\x00')
    tmp = "{0}.{1}".format(chunks[0].decode('latin-1'), chunks[1].decode('latin-1'))
    if tmp.endswith('.'):
        tmp = tmp[:-1]
    return tmp

HDR_BITMAP =  48
HDR_SPRITE =  32
HDR_MAP6   =   8
HDR_MAP7   =  16
PAL_SIZE   = 768
    
class LodArchive(object):
    '''Single lod archive class'''
   
    def __init__(self, filename):
        logging.config.fileConfig('conf/log.conf')
        self.log = logging.getLogger('LOD')
        self.lod_attr = {'filename' : filename }
        self.files = {}
        self.img_ext = "png"
        self.loaded = False
        
        try: # TODO use exteral exception handling
            if not self.lod_attr['filename'].lower().endswith(".lod"):
                raise TypeError('Lod file must end with \".lod\" extension')

            self.f = open(self.lod_attr['filename'], "rb")
            
            if self.f.read(4) != b"LOD\00":
                raise TypeError('File: \"{}\" is not a lod file'.format(self.lod_attr['filename']))
            
            self.log.info("Loading \"{0}\"".format(self.lod_attr['filename']))
            
            str_v = b''
            while True:
                str_v += self.f.read(1)
                if str_v[len(str_v)-1] == 0 or len(str_v) > 8:
                    break

            if b"MMVIII" in str_v:
                self.lod_attr['version'] = 8
            elif b"MMVII" in str_v:
                self.lod_attr['version'] = 7
            elif b"MMVI" in str_v:
                self.lod_attr['version'] = 6
            else:
                raise TypeError("\"{}\" file is corrupted can't read version!".format(self.lod_attr['filename']))
            
            self.f.seek(0x100)
            struct_fmt = '@16s4i' # char name[16]; int off,size,unk;
            s = struct.unpack_from(struct_fmt, self.f.read(struct.calcsize(struct_fmt)))
            self.lod_attr.update({'dirname': get_filename(s[0]), 'offset': s[1],
                             'size': s[2], 'unk': s[3], 'count': s[4]})
            self.log.info('''Lod version {}, internal directory: "{}", {} files.'''.
                       format(self.lod_attr['version'], self.lod_attr['dirname'], self.lod_attr['count']))
               
            if self.lod_attr['version'] == 8:
                struct_fmt = '@64s3i' # char name[64]; int off,size,unk;
                for i in range(self.lod_attr['count']):
                    s = struct.unpack_from(struct_fmt, self.f.read(struct.calcsize(struct_fmt)))
                    self.files[get_filename(s[0])] = { 'size' : s[2],'unk' : s[3],
                                                       'offset' : (s[1] + self.lod_attr['offset']) }
            else:
                struct_fmt = '@16s4i' # char name[16]; int off,size,unk,count;
                for i in range(self.lod_attr['count']):
                    s = struct.unpack_from(struct_fmt, self.f.read(struct.calcsize(struct_fmt)))
                    self.files[get_filename(s[0]).lower()] = { 'size' : s[2], 'unk' : s[3], 'count' : s[4],
                                                               'offset' : (s[1] + self.lod_attr['offset']) }
        except Exception as err:
            self.log.error("{}".format(err))
        self.loaded = True

    def GetFileData(self, dest, sfile):
        try:
            f_attr = self.files.get(sfile) # file attributes
            
            if f_attr is None:
                raise ValueError("File \"{}\" does not exists".format(sfile))
            
            self.log.debug("unpacking {} -> {}/{}".format(os.path.basename(self.lod_attr['filename']), self.lod_attr['dirname'], sfile))
            self.f.seek(f_attr['offset'])
            data = self.f.read(f_attr['size'])
            #save_file('{}/{}.item'.format(self.dest, sfile), data)
            
            if "bitmaps" in self.lod_attr['dirname'] or "icons" in self.lod_attr['dirname']:
                s = struct.unpack_from('@16sIIHHHHHHHHII', data[:HDR_BITMAP]) # char name[16]; int off,size,unk,count;
                f_attr.update({'fullname': get_full_filename(s[0]).lower(), 'size_img': s[1],
                               'size_compressed': s[2], 'size_uncompressed': s[11],
                               'w': s[3], 'h': s[4]})
                self.files[sfile].update(f_attr)
                if f_attr['size_img'] == 0: # file is not an image.
                    r_data = data[HDR_BITMAP:]
                    if r_data[:2] == b'\x78\x9c': # if it's compressed, decompress
                        r_data = zlib.decompress(r_data)
                        if f_attr['size_uncompressed'] != len(r_data):
                            raise "decompressed file does not match header information"
                    return {'data': r_data, 'name': f_attr['fullname']}
                else: # file is a "tga" image ( not really a tga )
                    dec_data = zlib.decompress(data[HDR_BITMAP:-PAL_SIZE])
                    if len(dec_data) != f_attr['size_uncompressed']:
                        raise("decompressed file \"{}\" size does not match header information".format(sfile))
                    self.f.seek((f_attr['offset'] + f_attr['size'] - PAL_SIZE))
                    return {'data': get_img(dec_data, f_attr['w'], f_attr['h']),
                            'img_size': (f_attr['w'], f_attr['h']),
                            'palette': self.f.read(PAL_SIZE)}
            elif "sprites" in self.lod_attr['dirname']:
                s = struct.unpack_from('@8sHHIHHHHHHI', data[:HDR_SPRITE]) # char name[8]; short unk[5] short w; int size;
                f_attr.update({'w': s[4], 'h': s[5], 'pal': s[6],
                                     'size_compressed': s[3], 
                                     'size_uncompressed': s[10]})
                self.files[sfile].update(f_attr)
                table_size = f_attr['h'] * 8
                table_data = data[HDR_SPRITE:(HDR_SPRITE+table_size)]
                dec_data = zlib.decompress(data[(table_size + HDR_SPRITE):])
                if f_attr['size_uncompressed'] != len(dec_data):
                    raise("decompressed file does not match header information")
                img_data = [0] * (f_attr['w'] * f_attr['h'])
                img_index = 0
                for i in range(f_attr['h']):
                    s = struct.unpack_from('@hhI', table_data, i*8) # short start,end; int offset
                    if s[0] != -1 and s[1] != -1:
                        for z in range(s[0]):
                            img_data[img_index] = 0
                            img_index += 1
                        dec_index = s[2]
                        for z in range(s[0], s[1]+1):
                            img_data[img_index] += dec_data[dec_index]
                            img_index += 1
                            dec_index += 1
                    for z in range(s[1], f_attr['w']-1):
                        img_data[img_index] = 0
                        img_index +=1
                palname = "{0}/palettes/pal{1:03d}.pal".format(dest, f_attr['pal'])
                if not os.path.isfile(palname):   #TODO load from lod.
                    raise("error can't find palette -> {}".format(palname))
                fpal = open(palname, "rb")
                paldata = fpal.read(PAL_SIZE)
                fpal.close()
                return {'data': get_img(array.array('B', img_data).tostring(), f_attr['w'], f_attr['h']),
                        'img_size': (f_attr['w'], f_attr['h']),
                        'palette': paldata }
            elif "maps" in self.lod_attr['dirname'] or "chapter" in self.lod_attr['dirname']:
                if data[:8] == b'\x41\x67\x01\x00\x6D\x76\x69\x69' and data[16:18] == b'\x78\x9C':
                    hdr_size = HDR_MAP7
                    s = struct.unpack_from('@IIII', data[:hdr_size])
                    f_attr.update({'version': 7, 'size_compressed': s[2],
                                              'size_uncompressed': s[3]})
                elif data[8:10] == b'\x78\x9C':
                    hdr_size = HDR_MAP6
                    s = struct.unpack_from('@II', data[:hdr_size])
                    f_attr.update({'version': 6, 'size_compressed': s[0],
                                         'size_uncompressed': s[1]})
                else:
                    return {'data': data, 'name': sfile}
                dec_data = zlib.decompress(data[hdr_size:])
                if f_attr['size_uncompressed'] != len(dec_data):
                    raise("decompressed file does not match header information")
                return {'data': dec_data, 'name': sfile}
            else:
                print("can't handle this directory")
        except ValueError as err:
            self.log.error("{}".format(err))
        except Exception as err:
            self.log.error("{}".format(err))
        return None

    def FileExists(self, sfile):
        return sfile in self.files.keys() # TODO exact search

    def GetFileList(self, filter=""):
        key_list = []
        for key in self.files.keys():
            if filter in key:
                key_list.append(key)
        return key_list

    def SaveFile(self, dest, sfile):
        ret = self.GetFileData(dest, sfile)
        if ret is None:
            return False
        if ret.get('img_size') is not None:
            img = Image.new("P", ret['img_size'])
            img.putdata(ret['data'])
            img.putpalette(ret['palette'])
            img.save('{}/{}.{}'.format(dest, sfile,self.img_ext))
        else:
            f = open('{}/{}'.format(dest, ret['name']), 'wb')
            f.write(ret['data'])
            f.close()
        return True

    def SaveFiles(self, dest, filter=""):
        failed = 0
        for sfile in self.files:
            if filter in sfile.lower() and not self.SaveFile(dest, sfile):
                failed += 1
        return failed   
