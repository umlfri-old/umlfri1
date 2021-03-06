from transform_matrix import TransformMatrix, PointMatrix
from exceptions import MathException

class PathPart(object):
    operation = None
    
    def GetOp(self):
        return self.operation
    
    def SetOp(self, value):
        self.operation = value
    
    def __str__(self):
        return ""
    
    def __repr__(self):
        return '<%s "%s">'%(self.__class__.__name__, self)

class PathPartMove(PathPart):
    operation = 'start'
    
    def __init__(self, point):
        if isinstance(point, PointMatrix):
            self.point = point
        else:
            self.point = PointMatrix.mk_xy(point)
    
    def GetFirstPos(self):
        return self.point
    
    def GetLastPos(self):
        return self.point
    
    def __iter__(self):
        yield self.point.GetIntPos()
    
    def __rmul__(self, other):
        if not isinstance(other, TransformMatrix):
            return NotImplemented
        ret = self.__class__(other*self.point)
        ret.SetOp(self.operation)
        
        return ret
    
    def __str__(self):
        return 'M %d,%d'%self.point.GetIntPos()

class PathPartLine(PathPart):
    operation = 'line'
    
    def __init__(self, point1, point2):
        if isinstance(point1, PointMatrix):
            self.point1 = point1
        else:
            self.point1 = PointMatrix.mk_xy(point1)
        if isinstance(point2, PointMatrix):
            self.point2 = point2
        else:
            self.point2 = PointMatrix.mk_xy(point2)
    
    def GetFirstPos(self):
        return self.point1
    
    def GetLastPos(self):
        return self.point2
    
    def __iter__(self):
        yield self.point2.GetIntPos()
    
    def __rmul__(self, other):
        if not isinstance(other, TransformMatrix):
            return NotImplemented
        ret = self.__class__(other*self.point1, other*self.point2)
        ret.SetOp(self.operation)
        
        return ret
    
    def __str__(self):
        return 'L %d,%d'%self.point2.GetIntPos()

class PathPartBezier(PathPart):
    operation = 'bezier'
    
    def __init__(self, point1, point2, point3, point4):
        if isinstance(point1, PointMatrix):
            self.point1 = point1
        else:
            self.point1 = PointMatrix.mk_xy(point1)
        if isinstance(point2, PointMatrix):
            self.point2 = point2
        else:
            self.point2 = PointMatrix.mk_xy(point2)
        if isinstance(point3, PointMatrix):
            self.point3 = point3
        else:
            self.point3 = PointMatrix.mk_xy(point3)
        if isinstance(point4, PointMatrix):
            self.point4 = point4
        else:
            self.point4 = PointMatrix.mk_xy(point4)
    
    def GetFirstPos(self):
        return self.point1
    
    def GetLastPos(self):
        return self.point4
    
    def __iter__(self):
        pt1 = self.point1.GetIntPos()
        pt2 = self.point2.GetIntPos()
        pt3 = self.point3.GetIntPos()
        pt4 = self.point4.GetIntPos()
        
        t = 0
        step = 1/16.0
        while (t-step) < 1:
            new = (1-t)**3*pt1[0]+3*t*(1-t)**2*pt2[0]+3*t**2*(1-t)*pt3[0]+t**3*pt4[0], \
                  (1-t)**3*pt1[1]+3*t*(1-t)**2*pt2[1]+3*t**2*(1-t)*pt3[1]+t**3*pt4[1]
            yield new
            t += step
        yield pt4
    
    def __rmul__(self, other):
        if not isinstance(other, TransformMatrix):
            return NotImplemented
        ret = self.__class__(other*self.point1, other*self.point2, other*self.point3, other*self.point4)
        ret.SetOp(self.operation)
        
        return ret
    
    def __str__(self):
        return 'C %d,%d %d,%d %d,%d'%(self.point2.GetIntPos()+self.point3.GetIntPos()+self.point4.GetIntPos())

class PathPartArc(PathPart):
    operation = 'arc'
    
    def __init__(self, point1, radius, rotation, flags, point2):
        if isinstance(point1, PointMatrix):
            self.point1 = point1
        else:
            self.point1 = PointMatrix.mk_xy(point1)
        self.radius = radius
        self.rotation = rotation
        self.flags = flags
        if isinstance(point2, PointMatrix):
            self.point2 = point2
        else:
            self.point2 = PointMatrix.mk_xy(point2)
    
    def GetFirstPos(self):
        return self.point1
    
    def GetLastPos(self):
        return self.point2
    
    def __iter__(self):
        raise NotImplementedError
    
    def __rmul__(self, other):
        raise NotImplementedError
    
    def __str__(self):
        return 'A %d,%d %d %d,%d %d,%d'%(self.radius+(self.rotation, int(self.flags[0]), int(self.flags[1]))+self.point2.GetIntPos())

class PathSingle(object):
    def __init__(self, path = None):
        if path is None:
            self.path = []
        else:
            self.path = path
    
    def append(self, part):
        self.path.append(part)
    
    def extend(self, other):
        self.path.extend(other.path)
    
    def __iter__(self):
        return (point for part in self.path for point in part)
    
    def __getitem__(self, index):
        if type(index) is slice:
            return self.__class__(self.path[index])
        else:
            return self.path[index]
    
    def __add__(self, other):
        if isinstance(other, PathSingle):
            return self.__class__(self.path+other.path)
        else:
            return self.__class__(self.path+other)
    
    def __rmul__(self, other):
        if not isinstance(other, TransformMatrix):
            return NotImplemented
        ret = []
        for part in self.path:
            ret.append(other*part)
        return self.__class__(ret)
    
    def __len__(self):
        return len(self.path)
    
    def GetType(self):
        if self.path[0].GetOp() == 'startstop':
            return 'polygon'
        else:
            return 'polyline'
    
    def __str__(self):
        if self.GetType() == 'polygon':
            xx = ' z'
        else:
            xx = ''
        return ' '.join([str(i) for i in self.path])+xx
    
    def __repr__(self):
        return '<%s "%s">'%(self.__class__.__name__, self)

class Path(object):
    def __init__(self, path):
        if isinstance(path, list):
            self.path = path
        else:
            self.path = self.__parsepath(path)
    
    def __popsur(self, arr):
        tmp = arr.pop(0).split(',')
        return (float(tmp[0]), float(tmp[1]))
    
    def __parsepath(self, path):
        ret = []
        path = path.split()
        ret2 = None
        while len(path) > 0:
            cmd = path.pop(0)
            if cmd == 'M':
                ret2 = PathSingle()
                ret.append(ret2)
                pt1 = self.__popsur(path)
                ret2.append(PathPartMove(pt1))
            else:
                if ret2 is None:
                    raise Exception, "First command of path in svg must be move (M)"
                if cmd in ('C', 'c'):
                    pt2 = self.__popsur(path)
                    pt3 = self.__popsur(path)
                    pt4 = self.__popsur(path)
                    if cmd == 'c':
                        pt2 = pt2[0]+pt1[0], pt2[1]+pt1[1]
                        pt3 = pt3[0]+pt1[0], pt3[1]+pt1[1]
                        pt4 = pt4[0]+pt1[0], pt4[1]+pt1[1]
                    ret2.append(PathPartBezier(pt1, pt2, pt3, pt4))
                    pt1 = pt4
                elif cmd in ('L', 'l'):
                    pt2 = self.__popsur(path)
                    if cmd == 'l':
                        pt2 = pt2[0]+pt1[0], pt2[1]+pt1[1]
                    ret2.append(PathPartLine(pt1, pt2))
                    pt1 = pt2
                elif cmd == 'z':
                    ret2[0].SetOp('startstop')
                    ret2 = None
        return ret
    
    def GetFirstPos(self):
        return self.path[0][0].GetFirstPos()
    
    def GetLastPos(self):
        return self.path[-1][-1].GetLastPos()
    
    def Flattern(self):
        ret = PathSingle()
        for path in self.path:
            if ret:
                if ret[-1].GetLastPos() == path[0].GetFirstPos():
                    if isinstance(path[0], PathPartMove):
                        ret.extend(path[1:])
                    else:
                        ret.extend(path)
                else:
                    ret.append(PathPartLine(ret[-1].GetLastPos(), path[0].GetFirstPos()))
                    ret.extend(path[1:])
            else:
                ret.extend(path)
        return self.__class__([ret])
    
    def Close(self, index = 0):
        self.path[index][0].SetOp('startstop')
    
    def __add__(self, other):
        if isinstance(other, Path):
            return self.__class__(self.path+other.path)
        elif isinstance(other, PathSingle):
            return self.__class__(self.path+[other])
        elif isinstance(other, PathPart):
            return self.__class__(self.path+[PathSingle([other])])
        else:
            return NotImplemented
    
    @classmethod
    def Join(cls, iterator):
        ret = []
        for other in iterator:
            if isinstance(other, Path):
                ret.extend(other.path)
            elif isinstance(other, PathSingle):
                ret.append(other)
            elif isinstance(other, PathPartMove):
                ret.append(PathSingle([other]))
            elif isinstance(other, PathPart):
                ret.append(PathSingle([PathPartMove(other.GetFirstPos()), other]))
        return cls(ret)
    
    def __rmul__(self, other):
        if not isinstance(other, TransformMatrix):
            return NotImplemented
        ret = []
        for path in self.path:
            ret.append(other*path)
        return self.__class__(ret)
    
    def __len__(self):
        return len(self.path)
    
    def __getitem__(self, index):
        if type(index) is slice:
            return self.__class__(self.path[index])
        else:
            return self.__class__([self.path[index]])
    
    def __iter__(self):
        return (single for single in self.path)
    
    def __str__(self):
        return ' '.join([str(i) for i in self.path])
    
    def __repr__(self):
        return '<%s "%s">'%(self.__class__.__name__, self)
