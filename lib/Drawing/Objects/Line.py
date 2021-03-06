from VisualObject import CVisualObject
from VBox import CVBox
from lib.datatypes import CColor

class CLine(CVisualObject):
    types = {
        'type': str,
        'color': CColor
    }
    def __init__(self, type = "auto", color = CColor("black")):
        CVisualObject.__init__(self)
        self.type = type
        self.color = color

    def __ComputeType(self):
        tp = self.type
        if tp == 'auto':
            if isinstance(self.parent, CVBox):
                tp = 'vertical'
            else:
                tp = 'horizontal'
        return tp

    def ComputeSize(self, context):
        tp = self.__ComputeType()
        if tp == 'horizontal':
            return (0, 1)
        else:
            return (1, 0)
    
    def GetResizable(self, context):
        tp = self.__ComputeType()
        return tp == 'horizontal', tp == 'vertical'

    def Paint(self, context, canvas):
        size = context.ComputeSize(self)
        tp = self.__ComputeType()
        pos = context.GetPos()
        size = context.GetSize()
        color = context.GetShadowColor()
        if color is None:
            color, = self.GetVariables(context, 'color')
        
        if tp == 'horizontal' and pos[0] is not None:
            canvas.DrawLine(pos, (pos[0]+size[0], pos[1]), color)
        elif tp == 'vertical' and pos[1] is not None:
            canvas.DrawLine(pos, (pos[0], pos[1]+size[1]), color)
