"""
Date: 2021-June-21
this utility is used to extract gps location information from all pictures under one folder and
show their physical locations,
use the latitude and longitude decimal coordinates extracted from pictures to query map.baidu.com
and get its physical locations
"""

try:
    import exifread
except ImportError:
    print('You need to install exifread 3rd party library by "pip install exifread"')
    exit(-1)
import re
import requests, json
import os,logging
import argparse


#
# original idea comes from :
#https://mp.weixin.qq.com/s?__biz=MjM5NzE1MDA0MQ==&mid=2247515082&idx=1&sn=513ed81e2f1ee20ab9a4dd93e4b5d615&chksm=a6dc97fc91ab1eea2fbe979aa768465c635fea86daf3c47dc274c79449ca7348737b97e7c588&mpshare=1&scene=1&srcid=0618IbkHOSuhqJgrc1rqkmQm&sharer_sharetime=1624000145242&sharer_shareid=5b5812d8e60ff7dbd282c4933514cf26#rd

class ExtractInfo:
    # experimental data for offset applied to original gps wgs-84 coordinate
    # before querying its actually physical position from baidu map
    # verified working well on June-21,2021 in Shanghai area
    LONG_OFF_BD = 0.011262
    LAT_OFF_BD = 0.004035   #0.003386
    BD_LOCATE_URL = 'http://api.map.baidu.com/lbsapi/getpoint/index.html'

    def __init__(self, pic_path, logger):
        self.pic_path = pic_path
        self.logger = logger

    def extract_image(self, pic_name):
        GPS = {}
        date = ''
        with open(self.pic_path+pic_name, 'rb') as f:
            tags = exifread.process_file(f)
            image_model = 'empty placeholder'
            for tag, value in tags.items():
                # 纬度
                if re.match('GPS GPSLatitudeRef', tag):
                    GPS['GPSLatitudeRef'] = str(value)
                # 经度
                elif re.match('GPS GPSLongitudeRef', tag):
                    GPS['GPSLongitudeRef'] = str(value)
                # 海拔
                elif re.match('GPS GPSAltitudeRef', tag):
                    GPS['GPSAltitudeRef'] = str(value)
                elif re.match('GPS GPSLatitude', tag):
                    try:
                        match_result = re.match('\[(\w*),(\w*),(\w.*)/(\w.*)\]', str(value)).groups()
                        GPS['GPSLatitude'] = int(match_result[0]), int(match_result[1]), int(match_result[2])
                    except:
                        deg, min, sec = [x.replace(' ', '') for x in str(value)[1:-1].split(',')]
                        GPS['GPSLatitude'] = self.__convert_coor(deg, min, sec)
    #                logger.debug("latitude={}".format(GPS['GPSLatitude']))
                elif re.match('GPS GPSLongitude', tag):
                    try:
                        match_result = re.match('\[(\w*),(\w*),(\w.*)/(\w.*)\]', str(value)).groups()
                        GPS['GPSLongitude'] = int(match_result[0]), int(match_result[1]), int(match_result[2])
                    except:
                        deg, min, sec = [x.replace(' ', '') for x in str(value)[1:-1].split(',')]
                        GPS['GPSLongitude'] = self.__convert_coor(deg, min, sec)
    #                logger.debug("longitude={}".format(GPS['GPSLongitude']))
                elif re.match('GPS GPSAltitude', tag):
                    GPS['GPSAltitude'] = str(value)
                elif re.match('GPS GPSProcessingMethod', tag):
                    # logger.debug(value)
                    # nonblanklist = [x.replace(' ','') for x in str(value)[1:-1].split(',')]
                    GPS['GPSProcessingMethod'] = str(value)
                elif re.match('Image Model', tag):
                    image_model = str(value)
                elif re.match('.*Date.*', tag):
                    date = str(value)
        return {'GPS_information': GPS, 'date_information': date, 'model': image_model}

    def __convert_coor(self, deg,minute,sec):
        """
        utility to convert degree,minute,second format coordinate to  decimal degree
        to be verified
        :param deg:
        :param min:
        :param sec:
        :return:
        """
        self.logger.debug('deg={},minute={},sec={}'.format(deg,minute,sec))
        try:
            decimal_degree = int(deg) + int(minute)/60 + eval(sec)/3600
        except ValueError:
            self.logger.error("invalid GPS degree,minute or seconds,return 0.000000")
            return 0.000000
        else:
            return round(decimal_degree, 6)

    def find_address_from_bd(self, GPS):
        secret_key = 'wLyevcXk5QY36hTKmvV5350F'
        if not GPS['GPS_information']:
            return '该照片无GPS信息'
        lat = round(GPS['GPS_information']['GPSLatitude']+ExtractInfo.LAT_OFF_BD, 6)
        lng = round(GPS['GPS_information']['GPSLongitude']+ExtractInfo.LONG_OFF_BD, 6)
        try:
            self.logger.info('True latitude,longitude are {},{},altitude={},date={}'
                        '\nBD-offset longitude,latitude are {},{},'
                        '\nGPSProcessingMethod={},PhoneModel={}'.format(
                GPS['GPS_information']['GPSLatitude'],GPS['GPS_information']['GPSLongitude'],
                GPS['GPS_information']['GPSAltitude'],GPS['date_information'],
                lng, lat, GPS['GPS_information']['GPSProcessingMethod'],
                GPS['model']))
        except KeyError:
            self.logger.info('True latitude,longitude are {},{},date={}'
                        '\nBD-offset longitude,latitude are {},{}'
                        '\nPhoneModel={}'.format(
                GPS['GPS_information']['GPSLatitude'],GPS['GPS_information']['GPSLongitude'],
                GPS['date_information'],
                lng, lat,
                GPS['model']))
            pass
        baidu_map_api = "http://api.map.baidu.com/geocoder/v2/?ak={0}&callback=renderReverse&location={1},{2}s&output=json&pois=0".format(
            secret_key, lat, lng)
        response = requests.get(baidu_map_api)
        content = response.text.replace("renderReverse&&renderReverse(", "")[:-1]
        baidu_map_address = json.loads(content)
        formatted_address = baidu_map_address["result"]["formatted_address"]
        province = baidu_map_address["result"]["addressComponent"]["province"]
        city = baidu_map_address["result"]["addressComponent"]["city"]
        district = baidu_map_address["result"]["addressComponent"]["district"]
        location = baidu_map_address["result"]["sematic_description"]

        return formatted_address, province, city, district, location




if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logHandler = logging.StreamHandler()
    logger.addHandler(logHandler)
    argparser = argparse.ArgumentParser(
        description="extract exif gps info from photoes and get physical location from baidu map,")
    argparser.add_argument("--path", dest='path', help='请指定照片文件所在的目录',
                           default='./', type=str)
    args = argparser.parse_args()
    pic_path = args.path
    logger.info("\nChecking all files under path:{}".format(pic_path))
    # pic_path = "/home/lijin/Pictures/locations/test/"
    extractInfo = ExtractInfo(pic_path, logger)
    list1 = os.listdir(pic_path)
    count = 1
    for pic_file_name in list1:
        try:
            logger.info("-"*25)
            gps_dict = extractInfo.extract_image(pic_file_name)

            result = extractInfo.find_address_from_bd(gps_dict)

            if result == "该照片无GPS信息":
                logger.info("No {}. The photo: {}  {}".format(count,pic_file_name, result))
            else:
                logger.info("No {}. The photo: {} was taken at {}".format(count,pic_file_name, result))
            count += 1
        except IsADirectoryError:
            pass

    logger.info("\n\nvisit http://api.map.baidu.com/lbsapi/getpoint/index.html , "
                "\npaste BD-offset longitude,latitude pair,选择 坐标反查，"
                "可以在地图上显示相应的地点")

