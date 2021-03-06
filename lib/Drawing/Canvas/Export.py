from lib.Depend.gtk2 import cairo, gtk

from cStringIO import StringIO

from CairoBase import CCairoBaseCanvas

import sys

class CExportCanvas(CCairoBaseCanvas):
    def __init__(self, storage = None, surface_type = None, filename = None, sizeX = 1000, sizeY = 1000, background = None ):
        self.surface_type = surface_type
        
        if filename == None:
            from os.path import expanduser
            self.filename = expanduser("~")
        else: 
            self.filename = filename

        #give filename proper encoding
        self.filename = self.filename.encode(sys.getfilesystemencoding())

        self.sizeX = sizeX 
        self.sizeY = sizeY

        if self.surface_type == 'pdf':
            if not cairo.HAS_PDF_SURFACE:
                raise ExportError ('cairo: no PDF support')
            self.surface = cairo.PDFSurface (self.filename, self.sizeX, self.sizeY)

        elif self.surface_type == 'svg':
            if not cairo.HAS_SVG_SURFACE:
                raise ExportError ('cairo: no SVG support')
            self.surface = cairo.SVGSurface (self.filename, self.sizeX, self.sizeY)

        elif self.surface_type == 'png' or self.surface_type == 'pixbuf' or self.surface_type == None:
            if not cairo.HAS_PNG_FUNCTIONS:
                raise ExportError ('cairo: no PNG support')
            self.surface = cairo.ImageSurface (cairo.FORMAT_ARGB32,self.sizeX, self.sizeY)

        elif self.surface_type == 'ps':
            if not cairo.HAS_PS_SURFACE:
                raise ExportError ('cairo: no PS support')
            self.surface = cairo.PSSurface (self.filename, self.sizeX, self.sizeY)
            cairo.PSSurface.dsc_comment(self.surface,"%%Title: uml.FRI diagram export");

        else :
            raise ExportError('unknown export surface or format')
        
        context = cairo.Context (self.surface)
        
        if background is not None:
            context.rectangle(0, 0, sizeX, sizeY)
            context.set_source_rgb(background.GetRed(), background.GetGreen(), background.GetBlue())
            context.fill()

        CCairoBaseCanvas.__init__(self, context, storage)

    #finish operations
    def Finish(self):
        if self.surface_type == 'png':
            self.surface.write_to_png (self.filename)
        
        if self.surface_type == 'pixbuf':
            f = StringIO()
            self.surface.write_to_png (f)
            self.surface.finish()
            loader = gtk.gdk.PixbufLoader()
            loader.write(f.getvalue())
            loader.close()
            return loader.get_pixbuf()
        
        self.surface.finish()
