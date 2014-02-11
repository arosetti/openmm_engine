#!/usr/bin/env python3
import sys, os, array, struct
import logging,logging.config
import zlib, pprint
from PIL import Image

HDR_BITMAP =  48
HDR_SPRITE =  32
HDR_MAP6   =   8
HDR_MAP7   =  16
PAL_SIZE   = 768

#################################### Functions #################################

def check_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def save_file(out, var):
    f = open( out, 'wb' )
    f.write( var )
    f.close()
    
def save_img(dest, data, palette, h, w):
    img = Image.frombytes("P", (h, w), data, "raw", "P", 0, 1)
    img.putpalette(palette)
    img.save(dest)

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

#################################### Main ######################################

if __name__ == "__main__":
    logging.config.fileConfig('conf/log.conf')
    logger = logging.getLogger('LOD')
    
    if len(sys.argv) != 2:
        print("usage: {} <file.lod> ".format(sys.argv[0]))
        sys.exit(1);

    check_dir('dest')
    lod_attr = {'filename' : sys.argv[1], 'failed': 0}
    files = {}

    try:
        if not lod_attr['filename'].lower().endswith(".lod"):
            logger.error("file must have \".lod\" extension")
            sys.exit(1) #TODO raise error
            
        f = open(lod_attr['filename'], "rb")
        
        if f.read(4) != b"LOD\00":
            sys.exit(1) #TODO raise error
        
        logger.info("loading \"{0}\"".format(lod_attr['filename']))
        
        str_v = b''
        while True:
            str_v += f.read(1)
            if str_v[len(str_v)-1] == 0 or len(str_v) > 8:
                break

        if b"MMVIII" in str_v:
            lod_attr['version'] = 8
        elif b"MMVII" in str_v:
            lod_attr['version'] = 7
        elif b"MMVI" in str_v:
            lod_attr['version'] = 6
        else:
            logger.error("\"{0}\" file is corrupted can't read version!".format(lod_attr['filename']))
            sys.exit(1) #TODO raise error
        
        logger.info("lod version {0}".format(lod_attr['version']))
        
        f.seek(0x100)
        struct_fmt = '@16s4i' # char name[16];	int off,size,unk,ù;
        s = struct.unpack_from(struct_fmt, f.read(struct.calcsize(struct_fmt)))
        lod_attr.update({'dirname': get_filename(s[0]), 'offset': s[1], 'size': s[2],
                    'unk': s[3], 'count': s[4]})
        logger.info("lod contains \"{0}\" files".format(lod_attr['count']))
           
        if lod_attr['version'] == 8:
            struct_fmt = '@64s3i' # char name[64]; int off,size,unk;
            for i in range(lod_attr['count']):
                s = struct.unpack_from(struct_fmt, f.read(struct.calcsize(struct_fmt)))
                files[get_filename(s[0])] = { 'offset' : (s[1] + lod_attr['offset']), 'size' : s[2], 'unk' : s[3] }
        else:
            struct_fmt = '@16s4i' # char name[16]; int off,size,unk,count;
            for i in range(lod_attr['count']):
                s = struct.unpack_from(struct_fmt, f.read(struct.calcsize(struct_fmt)))
                files[get_filename(s[0]).lower()] = { 'offset' : (s[1] + lod_attr['offset']), 'size' : s[2], 'unk' : s[3], 'count' : s[4] }

        for sfile in files:
            try:
                #if 'out01' not in sfile:
                #    continue
                logger.debug("loading {} -> {}/{}".format(lod_attr['filename'], lod_attr['dirname'],sfile))
                f.seek(files[sfile]['offset'])
                data = f.read(files[sfile]['size'])
                #save_file('dest/{0}.item'.format(sfile), data)
                
                if "bitmaps" in lod_attr['dirname'] or "icons" in lod_attr['dirname']:
                    s = struct.unpack_from('@16sIIHHHHHHHHII', data[:HDR_BITMAP]) # char name[16]; int off,size,unk,count;
                    files[sfile].update({'fullname': get_full_filename(s[0]).lower(), 'size_img': s[1],
                                         'size_compressed': s[2], 'size_uncompressed': s[11],
                                         'width': s[3], 'height': s[4]})
                    if files[sfile]['size_img'] == 0: # file is not an image.
                        r_data = data[HDR_BITMAP:]
                        if r_data[:2] == b'\x78\x9c': # if it's compressed, decompress
                            r_data = zlib.decompress(r_data)
                            if files[sfile]['size_uncompressed'] != len(r_data):
                                logger.debug("decompressed file does not match header information") #TODO raise err
                        save_file('dest/{}'.format(files[sfile]['fullname']), r_data)
                    else: # file is a "tga" image ( not really a tga )
                        dec_data = zlib.decompress(data[HDR_BITMAP:-PAL_SIZE])
                        if len(dec_data) != files[sfile]['size_uncompressed']:
                            logger.error("decompressed file \"{}\" size does not match header information".format(sfile))#TODO raise error
                        f.seek((files[sfile]['offset'] + files[sfile]['size'] - PAL_SIZE))
                        save_img('dest/{0}.bmp'.format(sfile),
                                 dec_data, f.read(PAL_SIZE),
                                 files[sfile]['width'], files[sfile]['height'])
                elif "sprites" in lod_attr['dirname']:
                    s = struct.unpack_from('@8sHHIHHHHHHI', data[:HDR_SPRITE]) # char name[8]; short unk[5] short width; int size;
                    files[sfile].update({'width': s[4], 'height': s[5], 'pal': s[6],
                                         'size_compressed': s[3], 
                                         'size_uncompressed': s[10]})
                    table_size = files[sfile]['height'] * 8
                    table_data = data[HDR_SPRITE:(HDR_SPRITE+table_size)]
                    dec_data = zlib.decompress(data[(table_size + HDR_SPRITE):])
                                  
                    if files[sfile]['size_uncompressed'] != len(dec_data):
                        logger.debug("decompressed file does not match header information") #TODO raise err
                    
                    img_data = [0] * (files[sfile]['width'] * files[sfile]['height'])
                    img_index = 0
                    for i in range(files[sfile]['height']):
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
                        for z in range(s[1], files[sfile]['width']-1):
                            img_data[img_index] = 0
                            img_index +=1
                    
                    palname = "dest/palettes/pal{0:0=3d}.pal".format(files[sfile]['pal'])
                    if not os.path.isfile(palname):   #TODO load from lod.
                        logger.error("error can't find palette -> {}".format(palname)) # TODO raise error
                        logger.error("[current limitation], extract BITMAPS.LOD and put all .pal files in \"dest/palettes\"")
                    fpal = open(palname, "rb")
                    save_img('dest/{0}.bmp'.format(sfile),
                             array.array('B', img_data).tostring(), fpal.read(PAL_SIZE),
                             files[sfile]['width'], files[sfile]['height'])
                    fpal.close()
                elif "maps" in lod_attr['dirname'] or "chapter" in lod_attr['dirname']:
                    if data[:8] == b'\x41\x67\x01\x00\x6D\x76\x69\x69' and data[16:18] == b'\x78\x9C':
                        hdr_size = HDR_MAP7
                        s = struct.unpack_from('@IIII', data[:hdr_size])
                        files[sfile].update({'version': 7, 'size_compressed': s[2],
                                             'size_uncompressed': s[3]})
                    elif data[8:10] == b'\x78\x9C':
                        hdr_size = HDR_MAP6
                        s = struct.unpack_from('@II', data[:hdr_size])
                        files[sfile].update({'version': 6, 'size_compressed': s[0],
                                             'size_uncompressed': s[1]})
                    else:
                        save_file('dest/{}'.format(sfile), data)
                        continue
                    dec_data = zlib.decompress(data[hdr_size:])
                    if files[sfile]['size_uncompressed'] != len(dec_data):
                        logger.debug("decompressed file does not match header information") #TODO raise err
                    save_file('dest/{}'.format(sfile), dec_data)
                else:
                    print("can't handle this directory")
            except:
                logger.error("{0}".format(sys.exc_info()))
                lod_attr['failed']+=1
                if len(data) > 0:
                    save_file('dest/{0}.failed'.format(sfile), data)
    except IOError as e:
        logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
    except:
        logger.error("{0}".format(sys.exc_info()))
    
    #pprint.pprint(files)
    pprint.pprint(lod_attr)
