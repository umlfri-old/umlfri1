from lib.Depend.gtk2 import gtk
from lib.Depend.gtk2 import pango

import os.path

from common import CWindow, event
from lib.Distconfig import IMAGES_PATH

gtk.rc_parse_string("""
    style "test"
    {
        bg_pixmap[NORMAL] = "<none>"
    } widget "frmSplash" style "test"
""")

class CfrmSplash(CWindow):
    name = 'frmSplash'
    glade = 'misc.glade'
    
    widgets = ('fixMain', 'lblVersion', )
    
    def __init__(self, app, wTree):
        CWindow.__init__(self, app, wTree)
        
        self.lblVersion.set_label(('<span foreground="white" font_desc="Arial bold 9">'+_("Version: %s")+'</span>')%self.application.GetVersionString())
        
        style = self.form.get_style().copy()
        pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_PATH, 'splash.png'))
        pixmap = gtk.gdk.Pixmap(self.form.window, pixbuf.get_width(), pixbuf.get_height())
        gc = self.fixMain.window.new_gc()
        pixbuf.render_to_drawable(pixmap, gc, 0, 0, 0, 0, -1, -1, 0, 0, 0)
        style.bg_pixmap[gtk.STATE_NORMAL] = pixmap
        self.form.set_style(style)
