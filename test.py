#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Simple labyrinth. 

This module contains the Labirynth class. The user navigates using arrow keys.
    
Author: vand@dtu.dk, 2020
Created on Fri Nov 27 09:57:29 2020


"""

import sys 
import PyQt5.QtCore  
import PyQt5.QtWidgets 
import PyQt5.QtGui

  
class Test(PyQt5.QtWidgets.QWidget):
    
    def __init__(self, scenary_filename=None):
 
        
        super().__init__() 
        
        if scenary_filename is None:
            print("Hello, no picture from you!")
            self.scenaryPix = PyQt5.QtGui.QPixmap(1500, 1200)
            self.scenaryPix.fill(PyQt5.QtGui.QColor(225,225,225,225))
        else:
            print("Hello, opening your picture!")
            self.scenaryPix = PyQt5.QtGui.QPixmap(scenary_filename)
        
        self.show()
        
    def paintEvent(self, event):
        """ Paint event for displaying the content of the widget."""
        painter_display = PyQt5.QtGui.QPainter(self) # this is painter used for display
        painter_display.setCompositionMode(
                    PyQt5.QtGui.QPainter.CompositionMode_SourceOver)
        painter_display.drawPixmap(self.rect(), self.scenaryPix)
       
    def closeEvent(self, event):
        print("Bye, I'm closing")
        PyQt5.QtWidgets.QApplication.quit()
        # hint from: https://stackoverflow.com/questions/54045134/pyqt5-gui-cant-be-close-from-spyder
        # should also check: https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder

        
      
if __name__ == '__main__':
          
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    if len(sys.argv)>1:
        filename = sys.argv[1]
        ex = Test(filename)
    else:
         ex = Test(scenary_filename='toppen_scenary.png')
    sys.exit(app.exec_())  
    
    
    
    