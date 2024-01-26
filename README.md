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

