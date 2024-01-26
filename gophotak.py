#!/usr/bin/env python3
'''
**********************************************************
* gophotak.py - Utility to sort out Google Photo Takeout *
**********************************************************

A Google Photos takeout results in some .tgz files that, when unpacked, result in
directories that each represent a year. In those directories you'll find the photos
(*.jpg) and he accompanying json files (*.jpg.json).
This program crawls through these directories and creates year and month 
subdirectories in the tatget directory, updates/adds EXIF data according to the
json files and original EXIF data, renames the photos according to the scheme: 
PHYYMMDDnr and places them in the correct year/month directory.
If two photoos are shot at the same second, the program will try to find the "subsecond" fields in
the EXIF data and use that to make the name unique. If there is no subsecond
to be found, or the name is still a duplicate, the program will extend the
name with "xn" where n is a unique sequence number which will start by 1 and
will be incremented until a unique filename is created.
Options:
-s - Source directory.
     Directory where the search for photos and belonging json files should start
     Default is current directory.
-t - Target directory.
     Directory where the photoos wull be placed in subdirectories according to
     the following scheme: /"Target dir"/Yyearnr/Mmonthnr/Ptimestamp
     subdirectories will be created when needed. 
-h - help
     Print this text

* If a photo without belongng json file is found report error
  Same goes for json file without photo
* Which formats (jpg, jpeg, png ...) are accepted?
* What to do with movies (mp4, mov, ...)?

> DL sep-oct 21 & jan22>
https://stackoverflow.com/questions/65045644/heic-to-jpeg-conversion-with-metadata 


'''

import os
import stat
import sys
import logging
from exif import Image
from datetime import datetime
import json
import sys
import shutil
import PythonMagick as pmag

# globals
SDIR = ''
TDIR = ''

def main():
    initprog()
    initscreen()
    input('Press enter to continu')
    dirwalk(SDIR)
    logging.info('%s ended', sys.argv[0])
        
def initprog():
    global SDIR, TDIR, OK
    logging.basicConfig(filename='GoPhoTak.log', 
                        encoding='utf-8', 
                        format='%(asctime)s %(levelname)s:%(message)s', 
                        level=logging.DEBUG)
    logging.info('%s started', sys.argv[0])

    if '-h' in sys.argv:
        showhelp()
        logging.info('Help wanted (-h), printed and exited')
        sys.exit()
    SDIR = os.getcwd()
    if '-s' in sys.argv:
        logging.info('-s: source directory specified')
        SDIR = sys.argv[sys.argv.index('-s') + 1]
        if not os.path.isdir(SDIR):
            logging.error('specified directory does not exist')
            logging.error('directory %s', SDIR)
            print('specified directory does not exist {}'.format(SDIR))
            sys.exit()
        SDIR = SDIR.rstrip('/')
    logging.info('source directory is %s', SDIR)
    TDIR = '/tmp/Fotoos'
    if '-t' in sys.argv:
        logging.info('-t: target directory specified')
        TDIR = sys.argv[sys.argv.index('-t') + 1]
        TDIR = TDIR.rstrip('/')
    if not os.path.isdir(TDIR):
        logging.info('create directory %s', TDIR)
        os.mkdir(TDIR)
        #PERMissions: 755
        PERM = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
        os.chmod(TDIR, PERM)
    logging.info('target directory is %s', TDIR)

def showhelp():
    help =     '''
**********************************************************
* gophotak.py - Utility to sort out Google Photo Takeout *
**********************************************************

A Google Photos takeout results in some .tgz files that, when unpacked, result in
directories that each represent a year. In those directories you'll find the photos
(*.jpg) and he accompanying json files (*.jpg.json).
This program crawls through these directories and creates year and month 
subdirectories in the tatget directory, updates/adds EXIF data according to the
json files and original EXIF data, renames the photos according to the scheme: 
PHYYMMDDnr and places them in the correct year/month directory.
Options:
-s - Source directory.
     Directory where the search for photos and belonging json files should start
     Default is current directory.
-t - Target directory.
     Directory where the photoos wull be placed in subdirectories according to
     the following scheme: /"Target dir"/Yyearnr/Mmonthnr/Ptimestamp
     subdirectories will be created when needed. If two photoos are shot at
     the same second, the program will try to find the "subsecond" fiels in
     the EXIF data and use that to make the name unique. If there is no subsecond
     to be found, or the name is still a duplicate, the program will extend the
     name with "xn" where n is a unique sequence number which will start by 1 and
     will be incremented until a unique filename is created.
-h - help
     Print this text
'''
    print(help)

def initscreen():
    print("\033c", end="")
    print("<" * 10 + " GoPhoTak " + ">" * 10)
    print("\nGoogle Photo's Takeout")
    print("\n\nSource Directory: {}".format(SDIR))
    print("Target Directory: {}".format(TDIR))
    print("\n\n\n" + "=" * 45 + "\n\n")

# process dir
#   all json files should be accompanied by a photo. Report errors.
    
def dirwalk(dir):
    for root, dirs, files in os.walk(dir, topdown=True):
        for name in files:
            if '.' in name:
                filename = os.path.join(root, name)
                suffix = name.rsplit(sep='.', maxsplit=1)[1]
                if suffix.upper() in ['HEIC', 'PNG']:
                    filename = migrtojpg(filename, suffix)
                    suffix = 'jpg'
                if suffix.upper() in ['JPG', 'JPEG'] :
                    processjpg(filename)

def migrtojpg(name, suffix):
    logging.info('Converting to JPG: %s', name)
    print("Convert {}: {}".format(suffix, name))
    im = pmag.Image(name)
    im.quality(100)
    im.magick('JPG')
    newname = name[:-(len(suffix)+1)] + '.jpg'
    im.write(newname)
    os.remove(name)
    jsonname = name + '.json'
    if os.path.isfile(jsonname):
        shutil.move(jsonname, name[:-(len(suffix)+1)] + '.jpg.json')
    return newname

def processjpg(name):
    print("Process JPG: {}".format(name))
    #process json, create/alter exif: https://auth0.com/blog/read-edit-exif-metadata-in-photos-with-python/ 
    # https://pypi.org/project/exif/
    # EXIF Tags: https://exiftool.org/TagNames/EXIF.html 
    with open(name, 'rb') as jpgfile:
        jpgimg = Image(jpgfile)
    timestamp, subsec = getjpgdate(name, jpgimg)
    if timestamp:
        movejpg(name, timestamp, subsec)

def getjpgdate(name, jpgimg):
    timestamp = None
    subsec = None
    if jpgimg.has_exif:
        timestamp = jpgimg.get('datetime_original', None)
        subsec = jpgimg.get('subsec_time_original', None)
    if timestamp:
        if timestamp.startswith('0000'):     # A few images with zero original timestamp
            timestamp = jpgimg.get('datetime', None) # bare datetime is better here
            subsec = None
            logging.info('%s got timestamp from datetime: %s', name, timestamp)
        if timestamp.startswith('0000'):     # Also zeroes in datetime? try json
            timestamp = None
    if not timestamp:
        jsonname = name + '.json'
        if not os.path.isfile(jsonname):
            if not fixedjson(name): # Will rename wrong named json files if they exist
                logging.error('No exif and no json for %s', name)
                return (None, None)
        with open(name + '.json') as jsonfile:
            data = json.load(jsonfile)
        if 'photoTakenTime' in data:
            ts = data['photoTakenTime']['timestamp']
            timestamp = datetime.fromtimestamp(int(ts)).strftime('%Y:%m:%d %H:%M:%S')
            logging.info('%s got timestamp from JSON photoTakenTime: %s', name, timestamp)
        else:
            logging.error('Unable to find photoTakenTime in json for %s', name)
            return (None, None)
    if timestamp.startswith('0000'): #Still zeroes? Keep for later.
        return (None, None)
    return (timestamp, subsec)

def fixedjson(name):
    '''
    Checks wether the jpg filename is in the format xxxxx(n).jpg
    In that case the json filename will be xxxxx.jpg(n).json
    In this case the function will rename the jsonfile to
    xxxxx(n).jpg.json and return True. This way it can be processed
    by the rest of the program.
    Returns False if the special filename format is not applicable.
    '''
    if name.endswith(').jpg'):
        for x in range(-6,-len(name)-1,-1): # work back from ')'
            if name[x] == '(':
                break
        else:  # fall through for loop
            return False
        oldname = name[:x] +  '.jpg' + name[x:len(name)-4] +'.json'
        newname = name + '.json'
        shutil.move(oldname, newname)
        logging.info('Renamed %s to %s', oldname, newname)
        return True
    else:
        print('no ).jpg at end')
        return False

def movejpg(name, timestamp, subsec):
    year = timestamp[0:4]
    month = timestamp[5:7]
    day = timestamp[8:10]
    hour = timestamp[11:13]
    minute = timestamp[14:16]
    second = timestamp[17:19]
    newname = ('P' +
              year  +
              month +
              day +
              hour +
              minute +
              '.jpg'
              )
    newmonth = os.path.join(TDIR, 'Y' + year, 'M' + month)
    if not os.path.exists(newmonth):
        os.makedirs(newmonth)
    newfile = os.path.join(newmonth, newname)
    if os.path.isfile(newfile):  #This photo already exists, make more specific
        logging.info('%s not unique, adding second %s', newfile, str(second))
        newfile = newfile[:-4] + second + '.jpg' #strip .jpg, append seconds, append .jpg
    if os.path.isfile(newfile):
        if not subsec is None:
            logging.info('%s still not unique, adding subsec %s', newfile, str(subsec))
            newfile = newfile[:-4] + subsec + '.jpg'    #append subsec (&strip/append .jpg)
        else:
            logging.info('%s still not unique, but no subsecs available', newfile)
    counter = 0
    while os.path.isfile(newfile): # Still not unique? Append or sequence number
        newfile = newfile[:-4]    # and increment until unique
        newfile = newfile.rsplit('x', maxsplit=1)[0] + 'x' + str(counter) + '.jpg'
        counter += 1
    if counter > 0:
        logging.info('Added sequence number to filename to make filename unique')
    # os.rename(name, newfile)   #does not work on different filesystems
    shutil.move(name, newfile)
    logging.info('%s moved to %s', name, newfile)
    jsonname = name + '.json'
    if os.path.isfile(jsonname):
        os.remove(jsonname)
        logging.info('%s removed', jsonname)

if __name__ == '__main__':
    main()
