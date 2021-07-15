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
#  baidu map api document
# https://lbsyun.baidu.com/index.php?title=uri/api/web
#
#http://api.map.baidu.com/marker?location=40.047669,116.313082&title=我的位置&content=百度奎科大厦&output=html&src=webapp.baidu.openAPIdemo
#//调起百度PC或web地图，且在（lat:39.916979519873，lng:116.41004950566）坐标点上显示名称"我的位置"，内容"百度奎科大厦"的信息窗口。
#https://lbsyun.baidu.com/index.php?title=uri/api/web

class ExtractInfo:
    # experimental data for offset applied to original gps wgs-84 coordinate
    # before querying its actually physical position from baidu map
    # verified working well on June-21,2021 in Shanghai area
    LONG_OFF_BD = 0.011262
    LAT_OFF_BD = 0.004035   #0.003386
    secret_key = 'QTzFTf0kvm8YuFYFCnNK3Xa5uQtgzbFM'   # baidu map ak  #'wLyevcXk5QY36hTKmvV5350F'
    BD_LOCATE_URL = 'http://api.map.baidu.com/marker?location={0},{1}' \
                    '&title={2}&content={3}&output=html&src=webapp.baidu.openAPIdemo&coord_type=wgs84'
    #坐标类型，可选参数。
        # 示例：
        # coord_type= bd09ll
        # 允许的值为：
        # bd09ll（百度经纬度坐标）
        # bd09mc（百度墨卡托坐标）
        # gcj02（经国测局加密的坐标)
        # wgs84（gps获取的原始坐标）

    #'http://api.map.baidu.com/lbsapi/getpoint/index.html'

    def __init__(self, pic_path, logger):
        self.pic_path = pic_path
        self.logger = logger

    def extract_image(self, pic_name):
        GPS = {}
        date_str = ''
        image_model = ''
        exif_version = ''
        try:
            with open(self.pic_path+pic_name, 'rb') as f:
                tags = exifread.process_file(f)

                for tag, value in tags.items():
                    #EXIF version
                    if re.match('EXIF ExifVersion',tag):
                        exif_version = str(value.printable)
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
                        self.logger.debug('original Altitude={}'.format(value.printable))
                        try:
                            GPS['GPSAltitude'] = "{:.2f}".format(eval(value.printable))
                        except ZeroDivisionError:
                            GPS['GPSAltitude'] = 0.0
                    elif re.match('GPS GPSProcessingMethod', tag):
                        GPS['GPSProcessingMethod'] = ''
                        for item in value.values:
                            try:
                                GPS['GPSProcessingMethod'] += (lambda x: chr(x) if x != 0 else ' ')(item)
                            except TypeError:   # for case when value.values is a string
                                GPS['GPSProcessingMethod'] = value.values
                                break
                    elif re.match('Image Model', tag):
                        image_model += (' ' + str(value))
                    elif re.match('Image Make', tag):
                        image_model += (' ' + str(value))
                    elif re.match('.*Date.*', tag):
                        date_str = str(value)
        except PermissionError:
            self.logger.error('one file has no permission,skip it')
            pass
        return {'GPS_information': GPS, 'date_information': date_str, 'model': image_model, 'exif_version': exif_version}

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
            decimal_degree = eval(deg) + eval(minute)/60 + eval(sec)/3600
        except (ValueError, ZeroDivisionError):
            self.logger.error("invalid GPS degree,minute or seconds,return 0.000000")
            return 0.000000
        else:
            return round(decimal_degree, 6)


    def wgs84_cord_conversion(self,GPS, targetCord = None):
        """
        https://lbsyun.baidu.com/index.php?title=webapi/guide/changeposition
        change wgs84 gps coordination to target coordination

        if targetCord is None, does not call baidu conversion api

        源坐标类型：

            1：GPS标准坐标（wgs84）；
            2：搜狗地图坐标；
            3：火星坐标（gcj02），即高德地图、腾讯地图和MapABC等地图使用的坐标；
            4：3中列举的地图坐标对应的墨卡托平面坐标;
            5：百度地图采用的经纬度坐标（bd09ll）；
            6：百度地图采用的墨卡托平面坐标（bd09mc）;
            7：图吧地图坐标；
            8：51地图坐标；

            目标坐标类型：

            3：火星坐标（gcj02），即高德地图、腾讯地图及MapABC等地图使用的坐标；
            5：百度地图采用的经纬度坐标（bd09ll）；
            6：百度地图采用的墨卡托平面坐标（bd09mc）；

            None:  do not need to convert

        :param GPS:
        :param targetCord: 坐标的类型，目前支持的坐标类型包括：bd09ll（百度经纬度坐标）、bd09mc（百度米制坐标）、gcj02ll（国测局经纬度坐标，仅限中国）、wgs84ll（ GPS经纬度）
        :return:  dict of x: longitude, y:latitude of bd09ll coordination
        """
        coord_mapping = {'wgs84ll': 1, 'gcj02': 3, 'bd09ll': 5, 'bd09mc': 6}
        GPS['GPS_information']['GPSLongitude'] = \
            (lambda x: (-1) * x if GPS['GPS_information']['GPSLongitudeRef'] == 'W' else x)(GPS['GPS_information']['GPSLongitude'])
        GPS['GPS_information']['GPSLatitude'] = \
            (lambda x: (-1) * x if GPS['GPS_information']['GPSLatitudeRef'] == 'S' else x)(GPS['GPS_information']['GPSLatitude'])

        if targetCord is None:
            return GPS['GPS_information']['GPSLongitude'], GPS['GPS_information']['GPSLatitude']
        else:
            try:
                baidu_coord_conversion_api = "http://api.map.baidu.com/geoconv/v1/?ak={0}&coords={1},{2}&from=1&to={3}".format(
                ExtractInfo.secret_key, GPS['GPS_information']['GPSLongitude'], GPS['GPS_information']['GPSLatitude'],
                coord_mapping[targetCord])

                response = requests.get(baidu_coord_conversion_api)
                text = json.loads(response.text)
                if text['status'] == 0:
                    return text['result'][0]['x'], text['result'][0]['y']
                else:
                    raise LookupError
            except:
                raise LookupError


    def find_address_from_bd(self, GPS):
        if GPS['exif_version'] == '':
            return '该照片无Exif信息'
        if not GPS['GPS_information'] and not GPS['date_information'] and not GPS['model']:
            return '该照片无地理位置信息'
        elif GPS['GPS_information']:
            try:
                lng, lat = self.wgs84_cord_conversion(GPS, None)        # use wgs84 coordination
            except LookupError:
                self.logger.error('wgs84 coordination to other coordination conversion failed,use wgs84')
                # lat = round(GPS['GPS_information']['GPSLatitude']+ExtractInfo.LAT_OFF_BD, 6)
                # lng = round(GPS['GPS_information']['GPSLongitude']+ExtractInfo.LONG_OFF_BD, 6)
                lat = round(GPS['GPS_information']['GPSLatitude'], 6)
                lng = round(GPS['GPS_information']['GPSLongitude'], 6)

            try:
                self.logger.info('True wgs84 latitude,longitude are {},{},altitude={},date={}'
                            '\nConverted longitude,latitude are {},{},'
                            '\nGPSProcessingMethod={},PhoneModel={}'.format(
                    GPS['GPS_information']['GPSLatitude'],GPS['GPS_information']['GPSLongitude'],
                    GPS['GPS_information']['GPSAltitude'],GPS['date_information'],
                    lng, lat, GPS['GPS_information']['GPSProcessingMethod'],
                    GPS['model']))
            except KeyError:
                self.logger.info('True wgs84 latitude,longitude are {},{},date={}'
                            '\nConverted longitude,latitude are {},{}'
                            '\nPhoneModel={}'.format(
                    GPS['GPS_information']['GPSLatitude'],GPS['GPS_information']['GPSLongitude'],
                    GPS['date_information'],
                    lng, lat,
                    GPS['model']))

            try:
                # baidu document for V3.0 , https://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding-abroad
                # use wgs84ll coordination to initiate reverse_geocoding query
                baidu_reverse_geocoding_api = "https://api.map.baidu.com/reverse_geocoding/v3/?ak={0}&" \
                                "coordtype=wgs84ll&location={1},{2}s&output=json&radius=500&extensions_poi=1".format(
                                ExtractInfo.secret_key, lat, lng)

                response = requests.get(baidu_reverse_geocoding_api)
                content = response.text
                baidu_map_address = json.loads(content)
                if baidu_map_address['status'] == 0:
                    formatted_address = baidu_map_address["result"]["formatted_address"]
                    province = baidu_map_address["result"]["addressComponent"]["province"]
                    city = baidu_map_address["result"]["addressComponent"]["city"]
                    district = baidu_map_address["result"]["addressComponent"]["district"]
                    location = baidu_map_address["result"]["sematic_description"]
                else:
                    self.logger.error(baidu_map_address['message'])
                    return 'unAuthorization baidu Id','unknown','unknown','unknown','unknown','unknown'


                # below is implementation of V2.0
                # baidu_map_api = "http://api.map.baidu.com/geocoder/v2/?ak={0}&callback=renderReverse&location={1},{2}s&output=json&pois=0".format(
                #     ExtractInfo.secret_key, lat, lng)
                # response = requests.get(baidu_map_api)
                # content = response.text.replace("renderReverse&&renderReverse(", "")[:-1]
                # baidu_map_address = json.loads(content)
                # formatted_address = baidu_map_address["result"]["formatted_address"]
                # province = baidu_map_address["result"]["addressComponent"]["province"]
                # city = baidu_map_address["result"]["addressComponent"]["city"]
                # district = baidu_map_address["result"]["addressComponent"]["district"]
                # location = baidu_map_address["result"]["sematic_description"]
            except:
                self.logger.error('error in connecting to baidu, please check you internet connection')
                return 'unknown','unknown','unknown','unknown','unknown','unknown'
            else:
                return formatted_address, province, city, district, location
        else:   # no GPS Location information, only model or date_information
            return 'unknown','unknown','unknown','unknown','unknown','unknown'




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

