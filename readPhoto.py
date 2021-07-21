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
from urllib.parse import urlencode
import queue
from threading import Thread, currentThread
from PIL import ImageTk
import zlib, base64

class ReadPhotoGui(Tk):
    HEIGHT = 800
    WIDTH = 1200
    os_dependency = {'Windows': WindowsOS, 'Linux': LinuxOS, 'Darwin': MacOS}
    icon = zlib.decompress(base64.b64decode(b'eJzt2U1u2zAQBWC6WnhpdNMtt132Bi56MetOvYCOoiNoqYUg1rF+Sc68x5rJbhgEQfIBDyDzEtMa5y7PD+e+vb7++u3cj+d3P5+f649Xl9efv99fX8Ox5keAi/l0r3SPfaz1G/aB+RV7z7yp8475pc5bV+fOPb7SZ+fule6RT9xhQcZ6hwUauMOCMO+f/zBqvOMOC8S8dbggJX4H7up8/nBf6aAgU4mDgjAfSxwUaChxUBDmffpy9cnevfzxtrcOF6TMveruU1wt0FzmakGmMlcLwnwsc7VAzIf1XvSu96s/vsi71e+V7hVvC10riPskVwo0l7pSEObT5kpBmI+lrhSI+bD7o9LvoveV3u3uK10uSFvsckGYu2IXCzSXu1gQ5tPhYkFqfTy5Jy4d0HByaQNnlxoUufAb7s8unHDkwp9A7PkOu8jzHcaeH2Ebe7bDxLMdJp4doUtWusPU0x2mnhzhnLpjHu9wyvxK/EI83uGY+414Qzza4SC4J37eYS/4hfj5CEU/7bCTvCF+OkLZjx22ol+JH0co87FDxW/EtyPM67euB3FPfD1CoX7rYr7sUKrXsq7EL8SXHUr1W9eNeEPcqfUr80av12t54qCee7xWvy0eOKzv/vsn8bqX1evtegZcv4a4J7799Sn1a4hv8Vq9AvaG+B6v1C9gb4gf8XL9Avbzy0uL40UP2KNXLxIvecAexQv188Sj+LxeDXFPPOK8fg1xTzzmrH7p9TL1JD6rV8Ce3V4TT+Pp3TP2/HIcexaf1C/j2IW7N4mPPedA4mcSP5P4GcdH9RPi/+etk/jWb8TxZ5f4VD/50cWA408u8lE/5clIj+OPesm8u/bkrsPxe/0U3lx9MNji+EDiA4mfSfxM4mccv9ZPjV9d5cXBY/kRxy+u86teaKw04PiXA/6oH5taofgPR/ysH56qdjieD03J0LbF8YHEBxIfSPx52fyfuM3/4bL5v83/sdv8n7jN/9XVk4tOrS/30Mfbvtwz75XuVSf3TJv/O1ggm//jgrSFbvN/cdn8f1u+0m3+Lyyb/5+Wzf9t/m/zf5v/2/zf5v/EYX1t/h9Q/Wz+D9zm//uy+T+Mt/k/jrf5P4y3+T+Ot/k/jLf5v83/4foHNP70SA=='))

    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.platform = platform.system()
        self.work_thread = None
        self.q = queue.Queue()
        self.buildInitialGui()

    def buildInitialGui(self):
        image = ImageTk.PhotoImage(data=ReadPhotoGui.icon)
        self.iconphoto(False, image)
        self.title("图片地理位置定位")
        self.resizable(True, True)
        self.geometry(str(ReadPhotoGui.WIDTH)+'x'+str(ReadPhotoGui.HEIGHT))

        frame_style = ttk.Style().configure("TFrame", background='lightgrey')
        self.mainframe = ttk.Frame(self, padding="1 1 1 1",
                                   relief=RAISED, style=frame_style,
                                   height=ReadPhotoGui.HEIGHT, width=ReadPhotoGui.WIDTH)
        # mainframe.grid_propagate(1)
        self.mainframe.pack(fill=BOTH, expand=True)
        # self.mainframe.columnconfigure(0,weight=1)
        self.top_frame = ttk.Frame(self.mainframe, padding="1 1 1 1", borderwidth=3,
                                   relief=GROOVE)
        self.top_frame.pack(side=TOP, fill=BOTH, expand=False)

        ttk.Label(self.top_frame, text='Path:').grid(row=0,column=0,sticky=(E,W), padx=10)
        self.path = StringVar()
        self.path.set('please select a folder where photos are placed')
        self.path_entry = ttk.Entry(self.top_frame, textvariable=self.path, width=80, state='disabled',justify='left')
        self.path_entry.grid(row=0, column=1, sticky=(E, W), padx=10)
        self.top_frame.columnconfigure(1, weight=1)  # set column #1 to use expanded space

        self.choose_button = ttk.Button(self.top_frame,text='Choose Directory',command=self.on_choose)
        self.choose_button.grid(row=0, column=2, sticky=(E, W),padx=20)

        self.about_button = ttk.Button(self.top_frame,text='About', state='normal',command=self.__on_about)
        self.about_button.grid(row=0, column=3, sticky=(E,W), padx=20, pady=10)

        # self.check_button = ttk.Button(self.top_frame, text='Analyze', command=self.on_check,state='disabled')
        # self.check_button.grid(row=0, column=3, sticky=(E,W),padx=20)

        # create a middle_frame to hold 2 buttons and a few labels
        self.middle_frame = ttk.Frame(self.mainframe, padding="1 1 1 1", borderwidth=3, relief=RIDGE)
        self.middle_frame.pack(fill=BOTH, expand=False, pady=5)     #fill horizontally, do NOT expand vertically
        self.show_button = ttk.Button(self.middle_frame,text='Open file', state='disabled', command=self.__on_show_pic)
        self.show_button.grid(row=0,column=4,sticky=(E,W), padx=40,pady=5)
        self.locate_button = ttk.Button(self.middle_frame,text='Locate on map', state='disabled',command=self.__on_locate)
        self.locate_button.grid(row=1, column=4, sticky=(E,W), padx=40,pady=5)



        ttk.Label(self.middle_frame, text='file(s) analyzed:').\
            grid(row=0,column=0,sticky=(E,W), padx=10, pady=10)
        self.total_count = IntVar()
        self.total_count.set(0)
        self.total_count_entry = ttk.Entry(self.middle_frame,
                textvariable=self.total_count,width=20,justify='left', state='disabled')
        self.total_count_entry.grid(row=0, column=1,sticky=(E,W),padx=10)

        ttk.Label(self.middle_frame, text='file(s) with GPS:').\
            grid(row=0,column=2,sticky=(E,W), padx=10, pady=10)
        self.gps_count = IntVar()
        self.gps_count.set(0)
        self.gps_count_entry = ttk.Entry(self.middle_frame,
                textvariable=self.gps_count,width=20,justify='left',state='disabled')
        self.gps_count_entry.grid(row=0, column=3,sticky=(E,W),padx=10)

        # place a progressbar
        style = ttk.Style()
        style.configure('Horizontal.TProgressbar', background='#5eba21')
        ttk.Label(self.middle_frame, text='Analysis Progress:')\
            .grid(row=1,column=0,sticky=(E,W), padx=10)
        self.progressbar = ttk.Progressbar(self.middle_frame, orient='horizontal',mode='determinate',value=0, maximum=100)
        self.progressbar.grid(row=1, column=1,columnspan=3, sticky=W+E)


        self.middle_frame.columnconfigure(1, weight=1)  # set column #1 to use expanded space
        self.middle_frame.columnconfigure(3, weight=1)  # and set column #3 to use expanded space

        self.notebook = ttk.Notebook(self.mainframe)
        self.notebook.pack(fill=BOTH, expand=True, pady=5)
        # whenever the selected tab changes, it generates following virtual event, and get handled by my routine
        self.notebook.bind("<<NotebookTabChanged>>", self.__notebook_tab_changed)

        self.frames_in_notebook = {}  # a dict to store  tabs'name and their handles
        #  eg. frames_in_notebook['GPS定位信息']['tab_handle']
        # eg.  frames_in_notebook['GPS定位信息']['tree_handle']

        self.selected_record = []



    def __clear_notebook(self):
        for tab_name in self.frames_in_notebook:
            # delete all children of this treeview
            children = self.frames_in_notebook[tab_name]['tree_handle'].get_children()
            for item in children:
                self.frames_in_notebook[tab_name]['tree_handle'].delete(item)

            # delete this tab in the notebook
            self.notebook.forget(self.frames_in_notebook[tab_name]['tab_handle'])

        self.frames_in_notebook.clear()



    def __periodic_check(self):
        while self.q.qsize():
            try:
                item_from_queue = self.q.get(block=True)
                self.logger.debug('{} get  item_from_queue is {}'.format(
                    currentThread().getName(), item_from_queue))

                # Do NOT call task_done too early here, otherwise, producer
                # thread will resume and generate more data into the queue,
                # MUST move it to the end of this consumer thread
                # self.q.task_done()

                # Do NOT add q.join() here!! otherwise, it will block this consumer thread
                # hence no q.task_done will be called, dead lock happens
                # self.q.join()

                if item_from_queue['result'] == "无Exif信息":
                    self.__fill_to_notebook(item_from_queue['noExifCount'],
                                             item_from_queue['filename'],
                                             item_from_queue['gps_dict'],
                                             item_from_queue['result'])
                elif item_from_queue['result'] == '无地理位置信息':
                    self.__fill_to_notebook(item_from_queue['noGPSInfoCount'],
                                             item_from_queue['filename'],
                                             item_from_queue['gps_dict'],
                                             item_from_queue['result'])
                else:
                    self.__fill_to_notebook(item_from_queue['count'],
                                             item_from_queue['filename'],
                                             item_from_queue['gps_dict'],
                                             item_from_queue['result'],
                                             gps_info=True)

            except queue.Empty:
                self.logger.debug('empty queue')
            except KeyError as e:
                # this is to handle case : incoming filename is a directory,
                # so no result is returned, only need to update GUI for current_percent
                self.logger.debug('unknown key:{}'.format(e))
            else:
                pass
            finally:
                # self.logger.debug('item_from_queue is {}'.format(item_from_queue))
                self.progressbar.configure(value=item_from_queue['current_percent'])
                self.total_count.set(item_from_queue['total_count'])
                self.gps_count.set(item_from_queue['count'])
                self.q.task_done()      # remember to call task_done() afterwards, it will resume producer thread
                self.q.join()       # whether or not call this to block myself, doesn't matter


        if self.work_thread is not None:
            if self.work_thread.is_alive():
                # self.logger.info('{} is alive'.format(self.work_thread.getName()))
                self.after(100, func=self.__periodic_check)
            else:
                self.logger.debug('work thread {} completes'.format(self.work_thread.getName()))
                self.work_thread.join()
                self.work_thread = None
                # self.progressbar.stop()



    def on_check(self):
        # self.check_button['state'] = 'disabled'
        self.progressbar.configure(value=0)
        self.logger.info("\nChecking all files under path:{}".format(self.path.get()))

        self.extractInfo = ExtractInfo(self.path.get(), self.logger)
        self.__clear_notebook()

        self.work_thread = Thread(target=analysis_work, name='AnalysisThread', daemon=True,
                                  args=(self.extractInfo, self.q, self.logger))
        self.work_thread.start()
        self.__periodic_check()



    # bind the notebook tab changed event
    def __notebook_tab_changed(self, event):
        """
        whenever user change to a different tab,
        clear all previous selected items in all notebook tabs, to avoid misunderstanding
        disable 2 buttons(show_button,locate_button)
        :param event:
        :return:
        """
        try:
            tab_label = self.notebook.tab(self.notebook.select(), 'text')
        except TclError as e:
            logger.info('ignore TclError:{}'.format(e))
        else:
            self.selected_record = None
            for tab_key in self.frames_in_notebook:
                if tab_key == tab_label:
                    continue
                else:
                    tree = self.frames_in_notebook[tab_key]['tree_handle']
                    tree.selection_remove(tree.selection()) # unselect previous selection

            self.locate_button.configure(state='disabled')
            self.show_button.configure(state='disabled')



    # bind the select event within a treeview
    def __item_selected(self, event):
        tab_label = self.notebook.tab(self.notebook.select(),'text')
        tree = self.frames_in_notebook[tab_label]['tree_handle']
        for selected_item in tree.selection():
            # dictionary
            item = tree.item(selected_item)
            # list
            self.selected_record = item['values']
            self.show_button.configure(state='normal')
            if tab_label == 'GPS定位信息':
                self.locate_button.configure(state='normal')
            else:
                self.locate_button.configure(state='disabled')

            # msgbox.showinfo(title='Information',
            #          message=','.join(self.selected_record[1:]))

    #bind mouse left key double click with a treeview
    def __double_clicked_treeview(self,event):
        self.__item_selected(event)
        self.__on_show_pic()
        
    #bind mouse right key click with a treeview
    def __right_clicked_treeview(self,event):
        self.__item_selected(event)
        tab_label = self.notebook.tab(self.notebook.select(),'text')
        # copy to system clipboard
        self.clipboard_clear()
        self.clipboard_append(str(self.selected_record))

        if tab_label == 'GPS定位信息':
            self.__on_locate()
        else:
            msgbox.showwarning("Alert", 'This record has been copied to system clipboard.\n\n'
                                     'You can only show photo location on map for a photo with GPS info')
            
        
    def  __treeview_sort_column(self, tv, col, reverse): #Treeview、列名、排列方式
        # ————————————————
        # 版权声明：本文为CSDN博主「超自然祈祷」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
        # 原文链接：https://blog.csdn.net/sinat_27382047/article/details/80161637
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        #print(tv.get_children(''))
        l.sort(reverse=reverse)     #排序方式
        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):        #根据排序后索引移动
            tv.move(k, '', index)
        #    print(k)
        tv.heading(col, command=lambda: self.__treeview_sort_column(tv, col, not reverse))#重写标题，使之成为再点倒序的标题

    def __fill_to_notebook(self,local_count, pic_file_name, gps_dict, result, gps_info=False):
        """

        :param local_count:  index int within this tab(category)
        :param pic_file_name:
        :param gps_dict:
        :param result: the name of a tab in the notebook
        :return:

        """
        decode_info = result
        if gps_info:
            result = 'GPS定位信息'  #set tab label


        tab_handle = self.frames_in_notebook.get(result)
        if tab_handle is None:
            # this category does not exist, then create a tab using result as the dictionary's key
            # store its tab_handle and tree_handle into a dict, so handles can be retrieved to operate tab and tree.
            frame_t = ttk.Frame(self.notebook)
            self.frames_in_notebook[result] = dict(tab_handle=frame_t, tree_handle=None)
            self.notebook.add(frame_t, text=result)

            # configure rows and columns expansion behaviour , how those rows and columns spread to take additional space
            for i in range(30):
                frame_t.rowconfigure(i,weight=1)
            for i in (0,):       #  columns 1# do not expand,which is y_scrollbar,only column 0# the treeview can expand
                frame_t.columnconfigure(i, weight=1)

            # add a treeView inside this frame
            if gps_info:
                columns = ['No','filename','model','date', 'address','country',
                         'province','city','location','method','altitude','longitude','latitude']
            else:
                columns = ['No', 'filename', 'model', 'date']
            # create a treeview, only a single item can be selected at a time
            # all columns are  displayed on tree view
            # specify the number of rows which are visible to 29
            tree = ttk.Treeview(frame_t, columns=columns, show='headings',
                                selectmode='browse', displaycolumns=columns,
                                height=29)

            self.frames_in_notebook[result]['tree_handle'] = tree

            #set treeview's columns property(name,width in pixel,justify, etc)
            tree.column('#0', width=0, stretch=NO)
            tree.column('No', anchor=CENTER, width=28,stretch=NO)
            tree.column('filename', anchor=CENTER, width=280)
            tree.column('model', anchor=CENTER, width=180)
            tree.column('date', anchor=CENTER, width=150)
            if gps_info: # add more columns
                tree.column('address', anchor=CENTER, width=180)
                tree.column('country', anchor=CENTER, width=80)
                tree.column('province', anchor=CENTER, width=80)
                tree.column('city', anchor=CENTER, width=80)
                tree.column('location', anchor=CENTER, width=280)
                tree.column('method', anchor=CENTER, width=100)
                tree.column('altitude', anchor=CENTER, width=80, stretch=NO)
                tree.column('longitude', anchor=CENTER, width=150, stretch=NO)
                tree.column('latitude', anchor=CENTER, width=150, stretch=NO)

            # set treeview's headings which are displayed as the first row
            tree.heading('#0', text='', anchor=CENTER)
            tree.heading('No', text='No.', anchor=CENTER,
                         command=lambda: self.__treeview_sort_column(tree,'No',False))
            tree.heading('filename', text='File name', anchor=CENTER,
                         command=lambda: self.__treeview_sort_column(tree,'filename',False))
            tree.heading('model', text='Model',anchor=CENTER,
                         command=lambda: self.__treeview_sort_column(tree, 'model', False))
            tree.heading('date', text='Date',anchor=CENTER,
                         command=lambda: self.__treeview_sort_column(tree, 'date', False))
            if gps_info:
                tree.heading('address', text='Address',anchor=CENTER,
                             command=lambda: self.__treeview_sort_column(tree, 'address', False))
                tree.heading('country',text='Country',anchor=CENTER,
                             command=lambda: self.__treeview_sort_column(tree, 'country', False))
                tree.heading('province',text='Province',anchor=CENTER,
                             command=lambda: self.__treeview_sort_column(tree, 'province', False))
                tree.heading('city', text='City',anchor=CENTER,
                             command=lambda: self.__treeview_sort_column(tree, 'city', False))
                tree.heading('location', text='Location',anchor=CENTER,
                             command=lambda: self.__treeview_sort_column(tree, 'location', False))
                tree.heading('method', text='GPS method',anchor=CENTER,
                             command=lambda: self.__treeview_sort_column(tree, 'method', False))
                tree.heading('altitude', text='Altitude',anchor=CENTER,
                             command=lambda: self.__treeview_sort_column(tree, 'altitude', False))
                tree.heading('longitude', text='Longitude',anchor=CENTER,
                             command=lambda: self.__treeview_sort_column(tree, 'longitude', False))
                tree.heading('latitude', text='Latitude',anchor=CENTER,
                             command=lambda: self.__treeview_sort_column(tree, 'latitude', False))

            tree.bind('<<TreeviewSelect>>', self.__item_selected)  # mouse left click to select 
            tree.bind('<Double-Button-1>',self.__double_clicked_treeview)  # mouse left double-click 
            tree.bind('<Button-3>',self.__right_clicked_treeview)   # mouse right click 
            
            # add a vertical scrollbar to the right of treeview
            y_scrollbar = ttk.Scrollbar(frame_t, orient=VERTICAL, command=tree.yview)
            self.frames_in_notebook[result]['yscroll_handle'] = y_scrollbar
            tree.configure(yscroll=y_scrollbar.set)
            y_scrollbar.grid(row=0, column=1, sticky='ns')

            # add a horizontal scrollbar to the bottom of treeview
            x_scrollbar = ttk.Scrollbar(frame_t, orient=HORIZONTAL, command=tree.xview)
            self.frames_in_notebook[result]['xscroll_handle'] = x_scrollbar
            tree.configure(xscroll=x_scrollbar.set)
            x_scrollbar.grid(row=1, column=0, sticky='ew')

        try:
            if gps_info:
                item_id = self.frames_in_notebook[result]['tree_handle'].insert('', END,
                    text='',values=(local_count,pic_file_name,gps_dict['model'],
                                    gps_dict['date_information'],decode_info[0],decode_info[1],
                                    decode_info[2],decode_info[3], decode_info[5],
                                    gps_dict['GPS_information']['GPSProcessingMethod'],
                                    gps_dict['GPS_information']['GPSAltitude'],
                                    gps_dict['GPS_information']['GPSLongitude'],
                                    gps_dict['GPS_information']['GPSLatitude']),open=False)
                # change gps treeview's maximum height to 29 to make horizontal scrollbar visible
                self.frames_in_notebook[result]['tree_handle'].configure(height=min(29, int(item_id.lstrip('I'),16)))
            else:
                self.frames_in_notebook[result]['tree_handle'].insert('', END,
                    text='',values=(local_count, pic_file_name, gps_dict['model'],
                                    gps_dict['date_information']),open=False)
        except KeyError as e:
            self.logger.error('missing key is :{}'.format(e))

        self.frames_in_notebook[result]['tree_handle'].grid(row=0, column=0, sticky='nsew')



    # def __fill_frame(self,count,filename,gps_dict,result):
    #     """
    #
    #     :param count:  seq number
    #     :param filename:  photo file name in string
    #     :param gps_dict:
    #     :param result:
    #     :return:
    #     """
    #     frame_t = ttk.Frame(self.notebook)
    #     self.frames_in_notebook.append(frame_t)
    #     self.notebook.add(frame_t, text=filename)
    #
    #     # configure rows and columns expansion behaviour , how those rows and columns spread to take additional space
    #     for i in range(7):
    #         frame_t.rowconfigure(i,weight=1)
    #     for i in (1,3):       # label columns 0#,2#, 4# do not expand
    #         frame_t.columnconfigure(i,weight=1)
    #
    #     file_var = StringVar()
    #     file_var.set(filename)
    #     self.file_vars.append(file_var)
    #     ttk.Label(frame_t,text='filename:').grid(row=0, column=0, padx=10, sticky=(E,W,N,S))
    #     ttk.Entry(frame_t,width=80,textvariable=self.file_vars[count], state='normal').\
    #         grid(row=0, column=1, columnspan=3, padx=10, sticky=(E,W,N,S))
    #     ttk.Button(frame_t,text='show photo',command=lambda:self.__on_show_pic(count)).\
    #         grid(row=0,column=4,padx=20,sticky=(E,W))
    #     locate_button = ttk.Button(frame_t,text='locate on baidu map',command=lambda:self.__on_locate(count))
    #     locate_button.grid(row=1,column=4, padx=20,sticky=(E, W))
    #
    #     # longitude
    #     ttk.Label(frame_t,text='longitude:').grid(row=1,column=0,padx=10,sticky=(E,W))
    #     longitude = StringVar()
    #     try:
    #         longitude.set('{:.6f}'.format(gps_dict['GPS_information']['GPSLongitude']))
    #     except KeyError:
    #         longitude.set('no longitute info')
    #         locate_button.configure(state='disabled')
    #     self.longitudes.append(longitude)
    #     ttk.Entry(frame_t,width=40, justify='left',textvariable=self.longitudes[count],).\
    #         grid(row=1,column=1,padx=10,sticky=(E,W))
    #
    #     # latitude
    #     ttk.Label(frame_t,text='latitude:').grid(row=1,column=2,padx=10,sticky=(E,W))
    #     latitude = StringVar()
    #     try:
    #         latitude.set('{:.6f}'.format(gps_dict['GPS_information']['GPSLatitude']))
    #     except KeyError:
    #         latitude.set('no latitude info')
    #         locate_button.configure(state='disabled')
    #     self.latitudes.append(latitude)
    #     ttk.Entry(frame_t,width=40,textvariable=self.latitudes[count]).\
    #         grid(row=1,column=3,padx=10,sticky=(E,W))
    #
    #     # altitude
    #     ttk.Label(frame_t,text='altitude:').grid(row=2,column=0,padx=10,sticky=(E,W))
    #     altitude = StringVar()
    #     try:
    #         altitude.set(gps_dict['GPS_information']['GPSAltitude'])
    #     except KeyError:
    #         altitude.set('no altitude info')
    #
    #     self.altitudes.append(altitude)
    #     ttk.Entry(frame_t,width=20,textvariable=self.altitudes[count]).grid(row=2,column=1,padx=10,sticky=(E,W))
    #
    #
    #     # GPSProcessingMethod
    #     ttk.Label(frame_t,text='Processing:').grid(row=2, column=2, padx=10, sticky=(E,W))
    #     processing = StringVar()
    #     try:
    #         processing.set(gps_dict['GPS_information']['GPSProcessingMethod'])
    #     except KeyError:
    #         processing.set('no GPS ProcessingMethod info')
    #
    #     self.processings.append(processing)
    #     ttk.Entry(frame_t,width=20,textvariable=self.processings[count]).grid(row=2,column=3,padx=10,sticky=(E,W))
    #
    #
    #     # date information
    #     ttk.Label(frame_t,text='date:').grid(row=3,column=0,padx=10,sticky=(E,W))
    #     date_var = StringVar()
    #     try:
    #         date_var.set(gps_dict['date_information'])
    #     except KeyError:
    #         date_var.set('no date information')
    #
    #     self.dates.append(date_var)
    #     ttk.Entry(frame_t,width=20,textvariable=self.dates[count]).grid(row=3,column=1,padx=10,sticky=(E,W))
    #
    #     # Model information
    #     ttk.Label(frame_t,text='Model:').grid(row=3,column=2,padx=10,sticky=(E,W))
    #     model_var = StringVar()
    #     try:
    #         model_var.set(gps_dict['model'])
    #     except KeyError:
    #         model_var.set('no model information')
    #
    #     self.models.append(model_var)
    #     ttk.Entry(frame_t,width=20,textvariable=self.models[count]).grid(row=3,column=3,padx=10,sticky=(E,W))
    #
    #     # Province information
    #     ttk.Label(frame_t,text='Province:').grid(row=4,column=0,padx=10,sticky=(E,W))
    #     province_var = StringVar()
    #     try:
    #         province_var.set(result[1])
    #     except IndexError:
    #         province_var.set('no province information')
    #
    #     self.provinces.append(province_var)
    #     ttk.Entry(frame_t,width=20,textvariable=self.provinces[count]).grid(row=4,column=1,padx=10,sticky=(E,W))
    #
    #     # city information
    #     ttk.Label(frame_t,text='City:').grid(row=4,column=2,padx=10,sticky=(E,W))
    #     city_var = StringVar()
    #     try:
    #         city_var.set(result[2])
    #     except IndexError:
    #         city_var.set('no city information')
    #
    #     self.cities.append(city_var)
    #     ttk.Entry(frame_t,width=20,textvariable=self.cities[count]).grid(row=4,column=3,padx=10,sticky=(E,W))
    #
    #     # district information
    #     ttk.Label(frame_t,text='District:').grid(row=5,column=0,padx=10,sticky=(E,W))
    #     district_var = StringVar()
    #     try:
    #         district_var.set(result[3])
    #     except IndexError:
    #         district_var.set('no district information')
    #
    #     self.districts.append(district_var)
    #     ttk.Entry(frame_t,width=20,textvariable=self.districts[count]).grid(row=5,column=1,padx=10,sticky=(E,W))
    #
    #
    #     # address information
    #     ttk.Label(frame_t,text='address:').grid(row=5,column=2,padx=10,sticky=(E,W))
    #     address_var = StringVar()
    #     try:
    #         address_var.set(result[0])
    #     except IndexError:
    #         address_var.set('no address information')
    #
    #     self.formatted_addrs.append(address_var)
    #     ttk.Entry(frame_t,width=20,textvariable=self.formatted_addrs[count]).grid(row=5,column=3,padx=10,sticky=(E,W))
    #
    #     # location information
    #     ttk.Label(frame_t,text='Location:').grid(row=6,column=0,padx=10,sticky=(E,W))
    #     location_var = StringVar()
    #     try:
    #         location_var.set(result[4])
    #     except IndexError:
    #         location_var.set('no detailed location information')
    #
    #     self.locations.append(location_var)
    #     ttk.Entry(frame_t,width=20,textvariable=self.locations[count]).grid(row=6,column=1,padx=10,sticky=(E,W))

    def __on_about(self):
        msgbox.showinfo("About","Preview Release (for friendly users ONLY) Ver: 1.2\n\n"
                                "Both feature requests and Bug reports are welcome\n\n\n"
                                "Date: July 21,2021\n\n"
                                "Author:topleaf_2000@hotmail.com"

                        )
    def __on_show_pic(self):
        ct = Context(ReadPhotoGui.os_dependency[self.platform],self.logger)
        ct.show_pic(self)

    def __on_locate(self):
        try:
            # get  latitude & longitude, which are the last 2 items in selected_record tuple
            # url_string = self.extractInfo.BD_LOCATE_URL.format(self.selected_record[-1], self.selected_record[-2],
            #                                 self.selected_record[1].split('.')[0][-9:].replace(' ', ''),"照片位置")
            country = self.selected_record[5]
            if country == 'CHN':
                bd_params = {
                    'location': str(self.selected_record[-1]) + ',' + str(self.selected_record[-2]),
                    # 'title': self.selected_record[1].split('.')[0][-9:].replace(' ', ''),
                    # 'content': '照片位置',
                    'output': 'html',
                    'src': 'webapp.baidu.openAPIDemo',
                    'coord_type': 'wgs84'
                }
                url_params = urlencode(bd_params, safe=',')
                # url_string = f"{self.extractInfo.BD_MARKER_ENDPOINT}?{url_params}"
                url_string = f"{self.extractInfo.BD_GEOCODER_ENDPOINT}?{url_params}"
            else:
                # https://developers.arcgis.com/rest/geocode/api-reference/geocode-coverage.htm#GUID-D61FB53E-32DF-4E0E-A1CC-473BA38A23C0
                arcgis_params = {
                    'location': str(self.selected_record[-2]) + ',' + str(self.selected_record[-1]),
                    'f': 'pjson',
                    'langCode': 'EN',  #'ZH'
                    # 'sourceCountry':'CHN',
                    'forStorage':'false',
                    'featureTypes':'' #'StreetInt'  # or ''
                }
                url_params = urlencode(arcgis_params)
                url_string = f"{self.extractInfo.ARCGIS_GEOCODER_ENDPOINT}?{url_params}"

        except (TypeError, IndexError):
            msgbox.showinfo('Information', 'Please select one file to locate it on map')
            return
        
        ct = Context(ReadPhotoGui.os_dependency[self.platform], self.logger)
        ct.show_on_baidu_map(url_string)



    def on_choose(self):
        """
        specify the folder where photos locate
        :return:
        """
        directory = filedialog.askdirectory(initialdir='/home/lijin/Pictures/locations/')
        while directory == '':
            msgbox.showerror("Choose Directory", 'you must specify a directory where photos exist')
            directory = filedialog.askdirectory()
        self.path.set(directory+'/')
        # self.check_button['state'] = 'normal'
        self.on_check()
        pass


def analysis_work(extractInfoInstance,progress_queue,logger):
    logger.debug('thread {} starts:'.format(currentThread().getName()))
    list1 = os.listdir(extractInfoInstance.get_path())
    list1.sort()
    list_len = len(list1)
    item_in_queue = {}

    noExifCount=0
    noGPSInfoCount=0
    count = 0
    totalCount = 0
    for i in range(list_len):
        try:
            logger.info("-"*25)
            item_in_queue.clear()
            gps_dict = extractInfoInstance.extract_image(list1[i])
            result = extractInfoInstance.find_address_from_bd(gps_dict)

            if result == "无Exif信息":
                logger.info("No {}. The photo: {}  {}".format(totalCount, list1[i], result))
                noExifCount += 1
            elif result == '无地理位置信息':
                logger.info("No {}. The photo: {}  {}".format(totalCount, list1[i], result))
                noGPSInfoCount += 1
            else:
                logger.info("No {}. The photo: {} was taken at {}".format(totalCount, list1[i], result))
                count += 1
            totalCount += 1

            item_in_queue['filename'] = list1[i]
            item_in_queue['result'] = result
            item_in_queue['gps_dict'] = gps_dict
        except IsADirectoryError:
            logger.debug('one directory file ignored')
        else:
            pass
        finally:
            item_in_queue['current_percent'] = "{:.1f}".format((i+1)/list_len*100)
            item_in_queue['total_count'] = totalCount
            item_in_queue['count'] = count
            item_in_queue['noExifCount'] = noExifCount
            item_in_queue['noGPSInfoCount'] = noGPSInfoCount

            progress_queue.put(item_in_queue)
            logger.debug('{} put one item (for filename) {} {} into queue'.format(currentThread().getName(),
                                                                   list1[i],
                                                                   item_in_queue['current_percent']))
            # https://www.cnblogs.com/dbf-/p/11118628.html
            # block current thread until all queue items have been get by consumer thread
            progress_queue.join()


    # logger.info("\n\nvisit http://api.map.baidu.com/lbsapi/getpoint/index.html , "
    #             "\npaste BD-offset longitude,latitude pair,选择 坐标反查，"
    #             "可以在地图上显示相应的地点")
    logger.debug('thread {} ends:'.format(currentThread().getName()))


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logHandler = logging.StreamHandler()
    logger.addHandler(logHandler)
    readPhoto = ReadPhotoGui(logger)
    # readPhoto.extract()
    readPhoto.mainloop()




