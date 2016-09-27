# -*- coding: utf-8 -*-

import win32com.client
import win32api
import win32con
import pythoncom


VK_CODE = {
    'spacebar': 0x20,
    'down_arrow': 0x28,
}

# This class implements slides control APIs.
class PPTControler:
    def __init__(self):
        # issue will raise for multithread http://www.cnblogs.com/AlgorithmDot/p/3386972.html
        pythoncom.CoInitialize()
        self.app = win32com.client.Dispatch("PowerPoint.Application")

    def openSlides(self, name):
        return self.app.Presentations.Open(name)

    def fullScreen(self):
        # full screen display
        if self.hasActivePresentation():
            self.app.ActivePresentation.SlideShowSettings.Run()
            #return self.getActivePresentationSlideIndex()

    def click(self):
        win32api.keybd_event(VK_CODE['spacebar'], 0, 0, 0)
        win32api.keybd_event(VK_CODE['spacebar'], 0, win32con.KEYEVENTF_KEYUP, 0)
        return self.getActivePresentationSlideIndex()

    def gotoSlide(self, index):
        # jump to a specified slide
        if self.hasActivePresentation():
            try:
                self.app.ActiveWindow.View.GotoSlide(index)
                return self.app.ActiveWindow.View.Slide.SlideIndex
            except:
                self.app.SlideShowWindows(1).View.GotoSlide(index)
                return self.app.SlideShowWindows(1).View.CurrentShowPosition

    def nextPage(self):
        if self.hasActivePresentation():
            count = self.getActivePresentationSlideCount()
            index = self.getActivePresentationSlideIndex()
            return index if index >= count else self.gotoSlide(index + 1)

    def prePage(self):
        if self.hasActivePresentation():
            index = self.getActivePresentationSlideIndex()
            return index if index <= 1 else self.gotoSlide(index - 1)

    def getActivePresentationSlideIndex(self):
        # get current page number of active presentation.
        if self.hasActivePresentation():
            try:
                index = self.app.ActiveWindow.View.Slide.SlideIndex
            except:
                index = self.app.SlideShowWindows(1).View.CurrentShowPosition
        return index

    def getActivePresentationSlideCount(self):
        # return total page count in current active presentation.
        return self.app.ActivePresentation.Slides.Count

    def getPresentationCount(self):
        # return all active presentation number
        return self.app.Presentations.Count

    def hasActivePresentation(self):
        # determine if there is any active presentation
        return True if self.getPresentationCount() > 0 else False



