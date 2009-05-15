# -*- coding: utf-8 -*-
from lib.Commands import CBaseCommand
from lib.Exceptions.DevException import HistoryError
import lib.consts

   


class CCommandProcessor:
    '''Class representing the application history, groups
    command objects and performs operations with them. 
    '''    
    
    def __init__(self):
        self.undoStack = []
        self.redoStack = []


    def __getStackDesc(self, redo = False, limitation = 0):
        '''
        Gets a description list from eather the redo or undo stack
        
        @param redo: True if redo descriptions are wanted, undo otherwise (by default)
        @type redo: bool

        @param limitation: number of command descriptions to be returned, if 0 return all
        @type limitation: int
        
        @return: list containing stack descriptions
        @rtype: list
        '''
        descriptionList = []
        
        if not redo:
            for undo in self.undoStack:
                descriptionList.append(str(undo))
        else:
            for redo in self.redoStack:
                descriptionList.append(str(redo))
            
        if limitation:
            return descriptionList[-limitation:]
        
        return descriptionList
 
 
    def add(self, commandObject):
        '''
        Adds a new object to applications history undo stack
        
        @param commandObject: instance to be added to undo stack  or group !
        @type type: L{CBaseCommand<lib.Commands.BaseCommand.CBaseCommand>} 
        '''
        
        if isinstance(commandObject, CBaseCommand):
            commandObject.do()                              # execute the command
            if commandObject.isEnabled():                   # if all went good...
                self.redoStack = []                         # emty the redo stack - linear restrictive undo
                self.undoStack.append(commandObject)        # and add the command to undo undo stack 
            
            # if the stack is bigger then the max allowed size, crop the oldest commands
            if len(self.undoStack) > lib.consts.STACK_MAX_SIZE:
                   self.undoStack = self.undoStack[-lib.consts.STACK_MAX_SIZE:]
          
        else: 
            raise HistoryError(_('Invalid Command object. Must be a child of lib.Commands.CBaseCommand'))


    def undo(self):
        '''
        Undo the last command in the undo stack
        and append it to the redo stack
        '''        
        if self.canUndo():
            undoStackItem = self.undoStack.pop()
            undoStackItem.undo()
            self.redoStack.append(undoStackItem)
            

    def redo(self):
        '''
        Redo the last command in the redo stack
        and append it to the undo stack
        '''                
        if self.canRedo():
            redoStackItem = self.redoStack.pop()
            redoStackItem.redo()       
            self.undoStack.append(redoStackItem)


    def getUndoDesc(self, limitation = 0):
        '''
        Gets a description list from the undo stack
       
        @param limitation: number of undo command descriptions to be returned, if 0 return all
        @type limitation: int
        
        @return: list containing the undo stack descriptions
        @rtype: list
        '''        
        return self.__getStackDesc(False, limitation)


    def getRedoDesc(self, limitation = 0):
        '''
        Gets a description list from the redo stack
       
        @param limitation: number of redo command descriptions to be returned, if 0 return all
        @type limitation: int
        
        @return: list containing the redo stack descriptions
        @rtype: list
        '''        
        return self.__getStackDesc(True, limitation)


    def canUndo(self):
        '''
        Returns true if undo can be performed

        @return: True if undo stack is not empty, else False
        @rtype: bool
        '''                
        return len(self.undoStack) > 0


    def canRedo(self):
        '''
        Returns true if redo can be performed

        @return: True if redo stack is not empty, else False
        @rtype: bool
        '''           
        return len(self.redoStack) > 0


    def clear(self):
        '''
        Clears the history - undo and redo stacks
        '''           
        self.undoStack = []
        self.redoStack = []
 
 

            