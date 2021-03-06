import gtk
import pygtk
from lib.Gui.frmPropertiesWidgets.Abstract.AbstractButton import CAbstractButton

class CButton(CAbstractButton):
    
    def __init__(self,title='', stock=None, tooltip=None):
        self.button=gtk.Button(title, stock)
        if tooltip: self.button.set_tooltip_text(tooltip)
        self.button.set_size_request(82,26)
        self.button.show()
    
    def GetWidget(self):
        return self.button
    
    def SetSize(self,x,y):
        self.button.set_size_request(x,y)
    
    def SetSensitive(self,value):
        self.button.set_sensitive(value)
    
    def GetSensitive(self):
        return self.button.get_property('sensitive')
    
    def SetHandler(self,event,func,data):
        if event=='clicked':
            self.button.connect('clicked',self.__ButtonEventHandler,func,data)
    
    def __ButtonEventHandler(self,button,func,data):
        if data!=None:
            func(*data)
        else:
            func()
    