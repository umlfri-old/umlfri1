import gtk, gobject

from lib.Drawing.Canvas.Gtk import PixmapFromPath

from common import CWidget, event

class CmnuItems(CWidget):
    name = 'mnuItems'
    widgets = ('mnuAddDiagram', )
    
    __gsignals__ = {
        'create-diagram':   (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
            (gobject.TYPE_STRING, ))
    }
        
    def Redraw(self):
        for item in self.mnuAddDiagram.get_children():
            self.mnuAddDiagram.remove(item)
        for diagram in self.application.Project.GetVersion().GetDiagrams():
            newItem = gtk.ImageMenuItem(diagram)
            newItem.connect("activate", self.on_mnuDiagrams_activate, diagram)
            img = gtk.Image()
            img.set_from_pixbuf(PixmapFromPath(self.application.Project.GetStorage(), self.application.Project.GetDiagramFactory().GetDiagram(diagram).GetIcon()))
            img.show()
            newItem.set_image(img)
            self.mnuAddDiagram.append(newItem)
            newItem.show()
        
    def on_mnuDiagrams_activate(self, widget, diagramId):
        self.emit('create-diagram', diagramId)
        
