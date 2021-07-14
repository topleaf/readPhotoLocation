from abc import ABC, abstractmethod
import os


class Context:
    def __init__(self, osHandler, logger):
        self.osHandler = osHandler
        self.logger = logger

    def show_pic(self, photoGui, count):
        self.logger.debug('Context.show_pic called')
        self.osHandler.show_pic(self, photoGui, count)

    def show_on_baidu_map(self,  url):
        self.logger.debug('Context.show_on_baidu_map called')
        self.osHandler.show_on_baidu_map(self, url)
        pass


class AbstractOSHandler(ABC):
    def __init__(self):
        super().__init__()
        pass

    @abstractmethod
    def show_pic(self, photoGui, count):
        raise NotImplemented

    @abstractmethod
    def show_on_baidu_map(self, url_string):
        raise NotImplemented


class WindowsOS(AbstractOSHandler):
    def __init__(self):
        super().__init__()

    def show_pic(self, photoGui, count):
        try:
            ret_v = os.system('"' + photoGui.path.get() + photoGui.file_vars[count].get() + '"')
            # in Windows OS, open a file whose name contains space, just ignore start and use double quotes
        except:
            self.logger.error('Windows system show_pic failure')
        else:
            if ret_v == 0:
                self.logger.info('Windows file opened: ' + photoGui.path.get() + photoGui.file_vars[count].get())
            else:
                self.logger.error('return value = {}'.format(ret_v))

    def show_on_baidu_map(self,  url_string):
        # in Windows OS, open a http link with & or space in the string, need to use following format
        #  refer to   https://ss64.com/nt/start.html
        calling_string = 'start ' + '"A fake title" "' + url_string + '"'
        try:
            self.logger.debug('windows os:'+ calling_string)
            ret_v = os.system(calling_string)
        except:
            self.logger.error('Windows system show_on_baidu_map failure')




class LinuxOS(AbstractOSHandler):
    def __init__(self):
        pass

    def show_pic(self, photoGui, count):
        try:
            ret_v = os.system('xdg-open ' + '"' + photoGui.path.get() + photoGui.file_vars[count].get() + '"')
        except:
            self.logger.error('linux system show_pic failure')
        else:
            if ret_v == 0:
                self.logger.info(' file opened: ' + photoGui.path.get() + photoGui.file_vars[count].get())
            else:
                self.logger.error('return value = {}'.format(ret_v))



    def show_on_baidu_map(self, url_string):
        try:
            self.logger.debug('Linux os show_on_baidu_map called')
            os.system('xdg-open ' + '"' + url_string + '"')
        except:
            self.logger.error('linux system show_on_baidu_map failure')
        else:
            self.logger.info('visit: ' + url_string)
        pass


class MacOS(AbstractOSHandler):
    def __init__(self):
        pass

    def show_pic(self, photoGui, count):
        try:
            ret_v = os.system('open ' + '"' + photoGui.path.get() + photoGui.file_vars[count].get() + '"')
        except:
            self.logger.error('MacOS system show_pic failure')
        else:
            if ret_v == 0:
                self.logger.info(' file opened: ' + photoGui.path.get() + photoGui.file_vars[count].get())
            else:
                self.logger.error('return value = {}'.format(ret_v))

    def show_on_baidu_map(self, url_string):
        try:
            os.system('open ' + '"' + url_string + '"')
        except:
            self.logger.error('MacOS system show_on_baidu_map failure')
        else:
            self.logger.info('visit: ' + url_string)
        pass

