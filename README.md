# readPhotoLocation
extract gps coordination from photoes and show their physical locations

prerequites:
1. internet connection to baidu.com
2. install python3 and pip package exifread

steps to run:
1. put all photoes you want to check location into one folder, ie, <myPhotoPath>
2. open a terminal, type:
python location.py --path <myPhotoPath>

this utility will return physical locations where the photoes were taken

you can put those photoes' BD-offset longitude,latitude values into  
http://api.map.baidu.com/lbsapi/getpoint/index.html
and show them on baidu map.

troubleshooting:
in case you see:
You need to install exifread 3rd party library by "pip install exifread"

you need to type
$pip install exifread
to install the dependency package at first,and retry

