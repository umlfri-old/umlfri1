from lib.Math2D import CPoint, CPolyLine, CLine
from math import pi, sqrt
from CacheableObject import CCacheableObject
from Context import CDrawingContext
import weakref

class EConLabelInfo(Exception): pass

class CConLabelInfo(CCacheableObject):
    '''
    Stores information about graphical representation of label
    '''
    
    def __init__(self, connection, position, logicalLabel):
        '''
        @param connection: owner of label
        @type  connection: L{CConection<Connection.CConnection>}
        
        @param position: initial position of label
        @type idx: string
        
        @param logicalLabel: reference to logical representation of label.
        @type logicalLabel: L{CVisualObject
        <lib.Drawing.Objects.VisualObject.CVisualObject>}
        '''
        
        CCacheableObject.__init__(self)
        self.idx = 0
        self.dist = 0
        self.pos = 0.5
        self.angle = pi/2
        self.position = position
        self.actualSize = (0, 0)
        self.connection = weakref.ref(connection)
        self.logicalLabel = logicalLabel
    
    def GetSaveInfo(self):
        '''Get information about self to be saved to .frip file
        
        This information can be used to restore values of attributes
        
        @return: dictionary containing essential information
        @rtype: dict
        '''
        return {\
            'idx': self.idx,
            'pos': self.pos,
            'dist': self.dist,
            'angle': self.angle}
    
    def SetSaveInfo(self, idx = 0, pos = 0.5, dist = 0, angle = pi/2):
        '''Get information about self to be saved to .frip file
        
        This information can be used to restore values of attributes
        
        @return: dictionary containing essential information
        @rtype: dict
        '''
        self.idx = int(idx)
        self.dist = float(dist)
        self.pos = float(pos)
        self.angle = float(angle)
        self.position = None
    
    def GetDiagram(self):
        '''
        @return: diagram to which belongs connection (owner)
        @rtype:  L{CDiagram<Diagram.CDiagram>}
        '''
        return self.connection().GetDiagram()
    
    def GetObject(self):
        '''
        @return: Logical Label Object
        @rtype: L{CConnectionObject<lib.Connections.Object.CConnectionObject>}
        '''
        return self.connection().GetObject()
    
    def GetConnection(self):
        return self.connection()
    
    def GetPosition(self):
        '''
        @return: absolute position of top-left corner in 2-tuple (x, y)
        @rtype: tuple
        '''
        width, height = self.GetSize()
        x, y = self.GetAbsolutePosition()
        x, y = x - width / 2.0, y - height / 2.0
        if x < 0 or y < 0:
            self.SetPosition((x, y))
        return int(max((0, x))), int(max((0, y)))
    
    def SetLogicalLabel(self, logicalLabel):
        '''
        Set reference to logical representation of label
        
        Real size of label cannot be known before this is set. Defaults to 
        (0, 0)
        
        @param logicalLabel: reference to logical representation of label.
        @type logicalLabel: L{CVisualObject
        <lib.Drawing.Objects.VisualObject.CVisualObject>}
        '''
        self.logicalLabel = logicalLabel
    
    def SetPosition(self, pos):
        '''
        Set absolute position of top-left corner of label
        
        @param pos: (x, y)
        @type  pos: tuple
        '''
        width, height = self.GetSize()
        pos = max((0, pos[0])), max((0, pos[1]))
        self.RecalculatePosition((pos[0] + width / 2.0, pos[1] + height / 2.0))
    
    def GetSize(self):
        '''
        @return: size of label in 2-tuple (width, height)
        @rtype:  tuple
        '''
        return self.actualSize
    
    def GetMinimalSize(self):
        '''
        The same as L{GetSize<self.GetSize>}.
        
        @return: size of label in 2-tuple (width, height)
        @rtype:  tuple
        '''
        return self.GetSize()
        
    def GetSquare(self):
        '''
        Get absolute position of rectangle to which label fits
        
        @return: ((left, top), (right, bottom)) positions of corners
        @rtype:  tuple
        '''
        
        width, height = self.GetSize()
        x, y = self.GetAbsolutePosition()
        
        return ( (int(x - width / 2.), int(y - height / 2.) ),
                 (int(x + width / 2.), int(y + height / 2.) ) )
    
    def GetAbsolutePosition(self):
        '''
        Get center position of label
        
        Center position is used for internal calculations relative to absolute
        and vice-versa
        
        @return: (x, y) position of the middle point of the label
        @rtype: tuple
        '''
        
        points = list(self.connection().GetPoints())
        angle = CLine(points[self.idx], points[self.idx + 1]).Angle()
        scaled = CLine(points[self.idx], points[self.idx + 1]).Scale(self.pos)
        return CLine.CreateAsVector(scaled.GetEnd(), 
            angle + self.angle, self.dist).GetEnd().GetPos()
    
    def RecalculatePosition(self, pos = None):
        '''
        Reset relative position so that label is bound to closest line segment
        of connection
        
        if pos is None then current position of label is used.
        
        @param pos: new absolute position (x, y) of label or None
        @type pos: tuple / NoneType
        '''
        x, y = (pos or self.GetAbsolutePosition())
        points = self.connection().GetPoints()
        self.idx, self.pos, self.dist, self.angle = \
            CPolyLine(tuple(points)).Nearest(CPoint((x, y)))
        
        self.GetPosition()
    
    def AreYouAtPosition(self, point):
        '''
        @return: True if (x, y) hits label
        @rtype: bool
        
        @param point: (x, y) position
        @type  point: tuple
        '''
        x, y = point
        ((x1, y1), (x2, y2)) = self.GetSquare()
        return x1 <= x <= x2 and y1 <= y <= y2
            
    def AreYouInRange(self, topleft, bottomright, all = False):
        '''
        Check wheter label is withinin rectangular area
        
        Can use two policy decision, depending on value of parameter all:
        
            - Whole label must be inside the rectangular area (all == True)
            - Label and rectangular area must have some intersection
        
        @return: True if label is in area
        @rtype: bool
        
        @param topleft: (x, y) position of top-left corner
        @type  topleft: tuple
        
        @param bottomright: (x, y) position of bottom-right corner
        @type  bottomright: tuple
        
        @param all: policy switch
        @type  all: bool
        '''
        
        class Test(object):
            def __init__(self, square):
                (self.x1, self.y1), (self.x2, self.y2) = square
            def __call__(self, pos):
                return self.x1 <= pos[0] <= self.x2 \
                    and self.y1 <= pos[1] <= self.y2
        
        t, l = topleft
        b, r = bottomright
        ((x1, y1), (x2, y2)) = self.GetSquare()
        if all:
            return l <= x1 <= x2 <= r and t <= y1 <= y2 <= b
        else:
            return (
                any( map( Test(((x1, y1), (x2, y2))), 
                    ((t,l),(t,r),(b,l),(b,r)))) or
                (x1 <= l <= r <= x2 and t <= y1 <= y2 <= b ) or
                (l <= x1 <= x2 <= r and y1 <= t <= b <= y2 ) )
    
    def SetToDefaultPosition(self, position):
        '''Set absolute and relative position according to default position
        defined by parameter position. Can be moved by offset by appending sign
        "+" or "-" and float number to recognized names of position.

        @param position: one of "center", "source", "destination"
        @type  position: str
        '''
        
        points = list(self.connection().GetPoints())
        if position.count('+'): # if there is offset specified
            position, offset = position.split('+', 1) # separate them
            try:
                offset = float(offset)
            except ValueError:
                raise EConLabelInfo('UndefinedOffset')
        elif position.count('-'): # offset as negative number
            position, offset = position.split('-', 1) # separate them
            try:
                offset = -float(offset)
            except ValueError:
                raise EConLabelInfo('UndefinedOffset')
        else:
            offset = None
        
        if position == 'source': # exactly at the very first point of the line
            self.idx = 0
            self.pos = 0.0
        elif position == 'destination': #exactly at the very last point of 
            self.idx = len(points) - 2
            self.pos = 1.0
        elif position == 'center':
            # find lenght of all parts of line as sum of lengths of distinct
            # parts
            lengths = [ sqrt( (points[i][0] - points[i+1][0])**2 +  
                                 (points[i][1] - points[i+1][1])**2 )
                           for i in xrange(len(points)-1) ]
            length = sum(lengths)
            if length == 0.0:
                self.idx = 0
                self.pos = 0.5
            else:
                i = 1 # index of part, where is the middle of the polyline
                half = length / 2.0
                while sum(lengths[:i]) < half:
                    i += 1
                # now update attributes
                self.idx = i-1
                if self.idx == 0:
                    self.pos = half / lengths[0]
                else:
                    self.pos = (half - sum(lengths[:i-1])) / lengths[i-1]
        else:
            raise EConLabelInfo("UndefinedPosition")
        self.dist = 0.0
        self.angle = 0.0
        if offset is not None:
            multi = -1 if (points[self.idx][1] - points[self.idx + 1][1]) * \
                (.5 - self.pos) > 0 else 1
            x, y = self.GetAbsolutePosition()
            self.RecalculatePosition((x, y + multi * offset * 15))

    def Paint(self, canvas):
        if self.position:
            self.SetToDefaultPosition(self.position)
            self.position = None

        context = CDrawingContext(self.connection(), (0,0))
        self.actualSize = self.logicalLabel.GetSize(context)

        (x, y) = self.GetPosition()

        context.SetPosition((x, y))

        self.logicalLabel.Paint(context, canvas)
