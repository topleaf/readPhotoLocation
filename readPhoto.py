# tkinter GUI to read geographic information from photos and display
# Date: July 2,2021
# Arthur: Jin Li

from tkinter import *
import tkinter.ttk as ttk

import context
from location import ExtractInfo
import logging
import os,platform
from tkinter import filedialog
import tkinter.messagebox as msgbox
from context import Context, WindowsOS, LinuxOS, MacOS

class ReadPhotoGui(Tk):
    HEIGHT = 300
    WIDTH = 1024
    os_dependency = {'Windows': WindowsOS, 'Linux': LinuxOS, 'Darwin': MacOS}

    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.platform = platform.system()
        self.buildInitialGui()

    def buildInitialGui(self):
        self.title("图片地理位置定位")
        self.resizable(True, True)
        self.geometry(str(ReadPhotoGui.WIDTH)+'x'+str(ReadPhotoGui.HEIGHT))

        ttk.Style().configure("TFrame", foreground='green', background='lightgrey')
        self.mainframe = ttk.Frame(self, padding="1 1 1 1",
                                   relief=RAISED,
                                   height=ReadPhotoGui.HEIGHT, width=ReadPhotoGui.WIDTH)
        # mainframe.grid_propagate(1)
        self.mainframe.pack(fill=BOTH, expand=True)
        # self.mainframe.columnconfigure(0,weight=1)
        self.top_frame = ttk.Frame(self.mainframe, padding="1 1 1 1", borderwidth=3,
                                   relief=GROOVE)
        self.top_frame.pack(side=TOP, fill=BOTH, expand=False)
        # self.bottom_frame = ttk.Frame(self.mainframe, padding="1 1 1 1", borderwidth=3,
        #                               relief=RIDGE)
        # self.bottom_frame.pack(fill=BOTH, expand=True)


        ttk.Label(self.top_frame, text='Path:').grid(row=0,column=0,sticky=(E,W), padx=10)
        self.path = StringVar()
        self.path.set('please choose folder where photos locate')
        self.path_entry = ttk.Entry(self.top_frame, textvariable=self.path, width=80, justify='left')
        self.path_entry.grid(row=0, column=1, sticky=(E, W), padx=10)
        self.top_frame.columnconfigure(1, weight=1)  # set column #1 to use expanded space

        self.choose_button = ttk.Button(self.top_frame,text='choose folder',command=self.on_choose)
        self.choose_button.grid(row=0, column=2, sticky=(E, W),padx=20)

        self.check_button = ttk.Button(self.top_frame, text='check', command=self.on_check,state='disabled')
        self.check_button.grid(row=0, column=3, sticky=(E,W),padx=20)

        self.notebook = ttk.Notebook(self.mainframe)
        self.frames_in_notebook = []
        self.file_vars = []
        self.longitudes =[]
        self.latitudes = []
        self.altitudes = []
        self.formatted_addrs = []
        self.provinces = []
        self.cities = []
        self.districts = []
        self.locations = []
        self.dates = []
        self.models = []
        self.processings = []


    def __clear_notebook(self):
        for frame_t in self.frames_in_notebook:
            self.notebook.forget(frame_t)
        self.frames_in_notebook.clear()
        self.file_vars.clear()
        self.longitudes.clear()
        self.latitudes.clear()
        self.altitudes.clear()
        self.formatted_addrs.clear()
        self.provinces.clear()
        self.cities.clear()
        self.districts.clear()
        self.locations.clear()
        self.dates.clear()
        self.models.clear()
        self.processings.clear()




    def on_check(self):
        self.check_button['state'] = 'disabled'
        self.logger.info("\nChecking all files under path:{}".format(self.path.get()))
        self.extractInfo = ExtractInfo(self.path.get(), self.logger)
        list1 = os.listdir(self.path.get())
        self.__clear_notebook()
        count = 0
        for pic_file_name in list1:
            try:
                self.logger.info("-"*25)
                gps_dict = self.extractInfo.extract_image(pic_file_name)


                result = self.extractInfo.find_address_from_bd(gps_dict)

                if result == "该照片无Exif信息":
                    self.logger.info("No {}. The photo: {}  {}".format(count,pic_file_name, result))
                else:
                    self.__fill_frame(count, pic_file_name,gps_dict,result)
                    self.logger.info("No {}. The photo: {} was taken at {}".format(count+1, pic_file_name, result))
                    count += 1
            except IsADirectoryError:
                pass

        logger.info("\n\nvisit http://api.map.baidu.com/lbsapi/getpoint/index.html , "
                    "\npaste BD-offset longitude,latitude pair,选择 坐标反查，"
                    "可以在地图上显示相应的地点")
        self.notebook.pack(fill=BOTH,expand=True,pady=5)

    def __fill_frame(self,count,filename,gps_dict,result):
        """

        :param count:  seq number
        :param filename:  photo file name in string
        :param gps_dict:
        :param result:
        :return:
        """
        frame_t = ttk.Frame(self.notebook)
        self.frames_in_notebook.append(frame_t)
        self.notebook.add(frame_t, text=filename)

        # configure rows and columns expansion behaviour , how those rows and columns spread to take additional space
        for i in range(7):
            frame_t.rowconfigure(i,weight=1)
        for i in (1,3):       # label columns 0#,2#, 4# do not expand
            frame_t.columnconfigure(i,weight=1)

        file_var = StringVar()
        file_var.set(filename)
        self.file_vars.append(file_var)
        ttk.Label(frame_t,text='filename:').grid(row=0, column=0, padx=10, sticky=(E,W,N,S))
        ttk.Entry(frame_t,width=80,textvariable=self.file_vars[count], state='normal').\
            grid(row=0, column=1, columnspan=3, padx=10, sticky=(E,W,N,S))
        ttk.Button(frame_t,text='show photo',command=lambda:self.__on_show_pic(count)).\
            grid(row=0,column=4,padx=20,sticky=(E,W))
        locate_button = ttk.Button(frame_t,text='locate on baidu map',command=lambda:self.__on_locate(count))
        locate_button.grid(row=1,column=4, padx=20,sticky=(E, W))

        # longitude
        ttk.Label(frame_t,text='longitude:').grid(row=1,column=0,padx=10,sticky=(E,W))
        longitude = StringVar()
        try:
            longitude.set('{:.6f}'.format(gps_dict['GPS_information']['GPSLongitude']))
        except KeyError:
            longitude.set('no longitute info')
            locate_button.configure(state='disabled')
        self.longitudes.append(longitude)
        ttk.Entry(frame_t,width=40, justify='left',textvariable=self.longitudes[count],).\
            grid(row=1,column=1,padx=10,sticky=(E,W))

        # latitude
        ttk.Label(frame_t,text='latitude:').grid(row=1,column=2,padx=10,sticky=(E,W))
        latitude = StringVar()
        try:
            latitude.set('{:.6f}'.format(gps_dict['GPS_information']['GPSLatitude']))
        except KeyError:
            latitude.set('no latitude info')
            locate_button.configure(state='disabled')
        self.latitudes.append(latitude)
        ttk.Entry(frame_t,width=40,textvariable=self.latitudes[count]).\
            grid(row=1,column=3,padx=10,sticky=(E,W))

        # altitude
        ttk.Label(frame_t,text='altitude:').grid(row=2,column=0,padx=10,sticky=(E,W))
        altitude = StringVar()
        try:
            altitude.set(gps_dict['GPS_information']['GPSAltitude'])
        except KeyError:
            altitude.set('no altitude info')

        self.altitudes.append(altitude)
        ttk.Entry(frame_t,width=20,textvariable=self.altitudes[count]).grid(row=2,column=1,padx=10,sticky=(E,W))


        # GPSProcessingMethod
        ttk.Label(frame_t,text='Processing:').grid(row=2, column=2, padx=10, sticky=(E,W))
        processing = StringVar()
        try:
            processing.set(gps_dict['GPS_information']['GPSProcessingMethod'])
        except KeyError:
            processing.set('no GPS ProcessingMethod info')
        
        self.processings.append(processing)
        ttk.Entry(frame_t,width=20,textvariable=self.processings[count]).grid(row=2,column=3,padx=10,sticky=(E,W))


        # date information
        ttk.Label(frame_t,text='date:').grid(row=3,column=0,padx=10,sticky=(E,W))
        date_var = StringVar()
        try:
            date_var.set(gps_dict['date_information'])
        except KeyError:
            date_var.set('no date information')

        self.dates.append(date_var)
        ttk.Entry(frame_t,width=20,textvariable=self.dates[count]).grid(row=3,column=1,padx=10,sticky=(E,W))

        # Model information
        ttk.Label(frame_t,text='Model:').grid(row=3,column=2,padx=10,sticky=(E,W))
        model_var = StringVar()
        try:
            model_var.set(gps_dict['model'])
        except KeyError:
            model_var.set('no model information')

        self.models.append(model_var)
        ttk.Entry(frame_t,width=20,textvariable=self.models[count]).grid(row=3,column=3,padx=10,sticky=(E,W))

        # Province information
        ttk.Label(frame_t,text='Province:').grid(row=4,column=0,padx=10,sticky=(E,W))
        province_var = StringVar()
        try:
            province_var.set(result[1])
        except IndexError:
            province_var.set('no province information')

        self.provinces.append(province_var)
        ttk.Entry(frame_t,width=20,textvariable=self.provinces[count]).grid(row=4,column=1,padx=10,sticky=(E,W))

        # city information
        ttk.Label(frame_t,text='City:').grid(row=4,column=2,padx=10,sticky=(E,W))
        city_var = StringVar()
        try:
            city_var.set(result[2])
        except IndexError:
            city_var.set('no city information')

        self.cities.append(city_var)
        ttk.Entry(frame_t,width=20,textvariable=self.cities[count]).grid(row=4,column=3,padx=10,sticky=(E,W))

        # district information
        ttk.Label(frame_t,text='District:').grid(row=5,column=0,padx=10,sticky=(E,W))
        district_var = StringVar()
        try:
            district_var.set(result[3])
        except IndexError:
            district_var.set('no district information')

        self.districts.append(district_var)
        ttk.Entry(frame_t,width=20,textvariable=self.districts[count]).grid(row=5,column=1,padx=10,sticky=(E,W))


        # address information
        ttk.Label(frame_t,text='address:').grid(row=5,column=2,padx=10,sticky=(E,W))
        address_var = StringVar()
        try:
            address_var.set(result[0])
        except IndexError:
            address_var.set('no address information')

        self.formatted_addrs.append(address_var)
        ttk.Entry(frame_t,width=20,textvariable=self.formatted_addrs[count]).grid(row=5,column=3,padx=10,sticky=(E,W))

        # location information
        ttk.Label(frame_t,text='Location:').grid(row=6,column=0,padx=10,sticky=(E,W))
        location_var = StringVar()
        try:
            location_var.set(result[4])
        except IndexError:
            location_var.set('no detailed location information')

        self.locations.append(location_var)
        ttk.Entry(frame_t,width=20,textvariable=self.locations[count]).grid(row=6,column=1,padx=10,sticky=(E,W))


    def __on_show_pic(self,count):
        ct = Context(ReadPhotoGui.os_dependency[self.platform],self.logger)
        ct.show_pic(self,  count)

    def __on_locate(self,count):
        url_string = self.extractInfo.BD_LOCATE_URL.format(self.latitudes[count].get(), self.longitudes[count].get(),
                                                       "照片位置", self.file_vars[count].get().split('.')[0][-9:].replace(' ', ''))
        # # url_string = self.extractInfo.BD_LOCATE_URL.format(self.latitudes[count].get(), self.longitudes[count].get(),
        #                                                "照片位置", 'here')
        ct = Context(ReadPhotoGui.os_dependency[self.platform], self.logger)
        ct.show_on_baidu_map(url_string)



    def on_choose(self):
        """
        specify the folder where photos locate
        :return:
        """
        directory = filedialog.askdirectory(initialdir='/home/lijin/Pictures/locations/')
        while directory == '':
            msgbox.showerror("Specify a folder",'you must specify a folder where photos exist')
            directory = filedialog.askdirectory()
        self.path.set(directory+'/')
        self.check_button['state'] = 'normal'
        pass

    def extract(self):

        list1 = os.listdir(self.path.get())
        count = 1
        for pic_file_name in list1:
            try:
                self.logger.info("-"*25)
                gps_dict = self.extractInfo.extract_image(pic_file_name)

                result = self.extractInfo.find_address_from_bd(gps_dict)

                if result == "该照片无GPS信息":
                    self.logger.info("No {}. The photo: {}  {}".format(count,pic_file_name, result))
                else:
                    self.logger.info("No {}. The photo: {} was taken at {}".format(count,pic_file_name, result))
                count += 1
            except IsADirectoryError:
                pass

        self.logger.info("\n\nvisit http://api.map.baidu.com/lbsapi/getpoint/index.html , "
                    "\npaste BD-offset longitude,latitude pair,选择 坐标反查，"
                    "可以在地图上显示相应的地点")
        self.logger.info("\n 或者使用 http://api.map.baidu.com/marker?location=40.047669,116.313082&title=我的位置&content=百度奎科大厦&output=html&src=webapp.baidu.openAPIdemo")

        pass


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logHandler = logging.StreamHandler()
    logger.addHandler(logHandler)
    readPhoto = ReadPhotoGui(logger)
    # readPhoto.extract()
    readPhoto.mainloop()




