from lib.Exceptions.UserException import *
import weakref

class CProjectNode(object):
    
    def __init__(self, parent = None, object = None, path = None):
        self.SetParent(parent)
        self.childs = []
        self.diagrams = []
        self.object = object
        if path is not None:
            self.object.SetPath(path)
        self.object.Assign(self)

    def Change(self):
        if self.GetParent() is not None:  
            parentPath = self.GetParent().GetPath()+ "/"
        else:
            parentPath = ""


        self.SetPath(parentPath + self.GetName() + ":" + self.GetType())
        for i in self.diagrams:
            i.SetPath(self.GetPath() + "/" +  i.GetName() + ":=Diagram=")
            
        for i in self.childs:
            i.Change()


    def GetAppears(self):
        return self.GetObject().GetAppears()

    def AddAppears(self, diagram):
        self.GetObject().AddAppears(diagram)

    def RemoveAppears(self, diagram):
        self.GetObject().RemoveAppears(diagram)

    def GetDiagrams(self):
        return self.diagrams

    def HasDiagram(self):
        return len(self.diagrams) > 0

    def GetPath(self):
        return self.object.GetPath()

    def SetPath(self, path):
        self.object.SetPath(path)

    def GetObject(self):
        return self.object

    def GetName(self):
        return self.object.GetName()

    def GetType(self):
        return self.object.GetType().GetId()

    def AddChild(self, child):
        if child not in self.childs:
            self.childs.append(child)
            child.SetParent(self)
            self.object.AddRevision()
        else:
            raise ProjectError("ExistsChild")


    def AddDiagram(self, diagram):
        if diagram not in self.diagrams:
            self.diagrams.append(diagram)
            diagram.Assign(self)
    
    def MoveDiagramToNewNode(self, newNode, diagram):
        self.RemoveDiagram(diagram)
        newNode.diagrams.append(diagram)
    
    def MoveNode(self, parentNode):
        self.GetParent().RemoveChild(self)
        self.SetParent(parentNode)
        parentNode.AddChild(self)
        self.SetPath(parentNode.GetPath() + "/" + self.GetPath().split('/')[-1])
    
    def FindDiagram(self, name):
        for i in self.diagrams:
            if i.GetName() == name:
                return i
        return None


    def GetChild(self, name, type):
        for i in self.childs:
            if i.GetName() == name and i.GetType() == type:
                return i
        else:
            return None

    def GetIndexChild(self, index):
        if index <= len(self.childs) - 1:
            return self.childs[index]
        else:
            raise ProjectError("NodeNotExists")

    def GetChilds(self):
        for i in self.childs:
            yield i

    def HasChild(self):
        return len(self.childs) > 0

    def GetParent(self):
        return self.parent()
        
    def SetParent(self,parent):
        if parent is None:
            self.parent = lambda: None
        else:
            self.parent = weakref.ref(parent) 

    def RemoveChild(self, child):
        if child in self.childs:
            self.childs.remove(child)
            self.object.AddRevision()
        else:
            raise ProjectError("ChildNotExists")

    def RemoveDiagram(self, diagram):
        if diagram in self.diagrams:
            self.diagrams.remove(diagram)
        else:
            raise ProjectError("AreaNotExists")

    Parent = property(GetParent,SetParent)