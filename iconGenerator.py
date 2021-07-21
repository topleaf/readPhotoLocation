# this is a utility to generate ico data from .ico file
# step 1: make a ico file using any ico editor
# step 2: read the data from the .ico file,
# step 3: compress the data to bytes object
# step 4. base64.b64encode the compressed bytes object data
#

# https://www.cnblogs.com/qianmaoliugou/p/11326555.html
from zlib import compress
from base64 import b64encode

if __name__ == '__main__':
    with open('/home/lijin/IdeaProjects/readPhotoLocation/256_location_place_service_green.ico','rb') as ico_source:
        b64bytes = b64encode(compress(ico_source.read()))

    with open('/home/lijin/IdeaProjects/readPhotoLocation/encodeIconData.py','w+') as ico_dest:
        ico_dest.write("img={0}".format(b64bytes))

    print('generation completes,copy and paste data from encodeIconData.py ')