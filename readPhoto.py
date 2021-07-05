# tkinter GUI to read geographic information from photos and display
# Date: July 2,2021
# Arthur: Jin Li

from tkinter import *
import tkinter.ttk as ttk

from location import ExtractInfo
import logging
import os
from tkinter import filedialog
import tkinter.messagebox as msgbox


class ReadPhotoGui(Tk):
    HEIGHT = 768
    WIDTH = 1024

    def __init__(self, logger):
        super().__init__()
        self.logger = logger

        self.buildInitialGui()
        # self.extractInfo = ExtractInfo(self.path, self.logger)


    def buildInitialGui(self):
        self.title = "read geographic information"
        self.resizable(True, True)
        self.geometry("1024x768")

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
        self.frames_in_notebook =[]
        self.file_vars = []
        self.longitudes =[]
        self.latitudes = []
        self.altitudes = []


        pass

    def on_check(self):
        self.check_button['state'] = 'disabled'
        self.logger.info("\nChecking all files under path:{}".format(self.path.get()))
        self.extractInfo = ExtractInfo(self.path.get(), self.logger)
        list1 = os.listdir(self.path.get())
        count = 0
        for pic_file_name in list1:
            try:
                self.logger.info("-"*25)
                gps_dict = self.extractInfo.extract_image(pic_file_name)


                result = self.extractInfo.find_address_from_bd(gps_dict)

                if result == "该照片无GPS信息":
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
        file_var = StringVar()
        file_var.set(filename)
        self.file_vars.append(file_var)
        ttk.Label(frame_t,text='filename:').grid(row=0,column=0, padx=10,sticky=(E,W))
        ttk.Entry(frame_t,width=80,textvariable=self.file_vars[count]).\
            grid(row=0,column=1,columnspan=3,padx=10,sticky=(E,W))
        ttk.Button(frame_t,text='show photo',command=lambda:self.__on_show_pic(filename)).\
            grid(row=0,column=4,padx=20,sticky=(E,W))
        ttk.Button(frame_t,text='locate',command=lambda:self.__on_locate(gps_dict)).\
            grid(row=0,column=5, padx=20,sticky=(E, W))

        ttk.Label(frame_t,text='longitude:').grid(row=1,column=0,padx=10,sticky=(E,W))
        longitude = StringVar()
        longitude.set('{:.6f}'.format(gps_dict['GPS_information']['GPSLongitude']))
        self.longitudes.append(longitude)
        ttk.Entry(frame_t,width=20,textvariable=self.longitudes[count]).\
            grid(row=1,column=1,padx=10,sticky=(E,W))

        ttk.Label(frame_t,text='latitude:').grid(row=1,column=2,padx=10,sticky=(E,W))
        latitude = StringVar()
        latitude.set('{:.6f}'.format(gps_dict['GPS_information']['GPSLatitude']))
        self.latitudes.append(latitude)
        ttk.Entry(frame_t,width=20,textvariable=self.latitudes[count]).grid(row=1,column=3,padx=10,sticky=(E,W))

        ttk.Label(frame_t,text='altitude:').grid(row=2,column=0,padx=10,sticky=(E,W))
        altitude = StringVar()
        try:
            altitude.set(gps_dict['GPS_information']['GPSAltitude'])
        except KeyError:
            altitude.set('no altitude info')

        self.altitudes.append(altitude)
        ttk.Entry(frame_t,width=20,textvariable=self.altitudes[count]).grid(row=2,column=1,padx=10,sticky=(E,W))

    def __on_show_pic(self,filename):
        os.system('xdg-open ' + self.path.get() + filename)
        self.logger.info(' file opened: ' + self.path.get() + filename)

    def __on_locate(self,gps_dict):
        os.system('xdg-open ' + self.extractInfo.BD_LOCATE_URL)
        self.logger.info('visit ' + self.extractInfo.BD_LOCATE_URL)

    def on_choose(self):
        """
        specify the folder where photos locate
        :return:
        """
        directory = filedialog.askdirectory(initialdir='/home/lijin/Pictures/locations/trial/wifi')
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

        pass


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logHandler = logging.StreamHandler()
    logger.addHandler(logHandler)
    readPhoto = ReadPhotoGui(logger)
    # readPhoto.extract()
    readPhoto.mainloop()




