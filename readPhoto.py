# tkinter GUI to read geographic information from photos and display
# Date: July 2,2021
# Arthur: Jin Li

from tkinter import *
import tkinter.ttk as ttk

from location import ExtractInfo
import logging
import os


class ReadPhoto(Tk):
    HEIGHT = 768
    WIDTH = 1024
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.title = "read photo geographic information"
        self.resizable(False,False)
        self.mainframe = ttk.Frame(self, padding="1 1 1 1", borderwidth=3, height=ReadPhoto.HEIGHT, width=ReadPhoto.WIDTH)
        # mainframe.grid_propagate(1)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.top_frame = ttk.Frame(self.mainframe, padding="1 1 1 1", borderwidth=3,
                                   height=ReadPhoto.HEIGHT/20, width=ReadPhoto.WIDTH)
        self.top_frame.grid(row=0,column=0, sticky=(N, W, E, S))
        self.bottom_frame = ttk.Frame(self.mainframe, padding="1 1 1 1", borderwidth=3,
                                      height=ReadPhoto.HEIGHT-ReadPhoto.HEIGHT/20, width=ReadPhoto.WIDTH)
        self.bottom_frame.grid(row=1,column=0, sticky=(N, W, E, S))

        ttk.Label(self.top_frame, text='Path:').grid(row=1,column=1,sticky=(E,W))
        self.path = StringVar()
        self.path_entry = ttk.Entry(self.top_frame, textvariable=self.path, justify='left')
        self.path_entry.grid(row=1, column=2, sticky=(E, W))

        self.choose_button = ttk.Button(self.top_frame,text='choose pic folder',command=self.on_choose)
        self.choose_button.grid(row=1, column=3, sticky=(E, W))

        self.check_button = ttk.Button(self.top_frame, text='check', command=self.on_check)
        self.check_button.grid(row=1, column=4, sticky=(E,W))

        self.buildInitialGui()
        self.extractInfo = ExtractInfo(self.path, self.logger)


    def buildInitialGui(self):

        pass

    def on_check(self,event):
        pass

    def on_choose(self):
        """
        specify the folder where photos locate
        :return:
        """
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
    readPhoto = ReadPhoto(logger)
    readPhoto.extract()
    readPhoto.mainloop()




