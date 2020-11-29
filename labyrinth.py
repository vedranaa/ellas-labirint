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
import numpy as np # this is just to transform example image to rgba
  
class Labyrinth(PyQt5.QtWidgets.QWidget):
    
    def __init__(self, scenary_filename=None, layout_filename=None, avatar_filename=None, start_pos=None):
        '''
        Initializes an Labyrinth without the image.

        Parameters
        ----------
        size : two-element tupple for the size of the labyrinth.

        '''
        
        super().__init__() 
        
        # Pixmap layers
        if scenary_filename is None:
            self.scenaryPix = PyQt5.QtGui.QPixmap(1500, 1200)
            self.scenaryPix.fill(PyQt5.QtGui.QColor(225,225,225,225))
        else:
            self.scenaryPix = PyQt5.QtGui.QPixmap(scenary_filename)
        
        if layout_filename is None:
            self.layoutImage = self.scenaryToLayout(self.scenaryPix)
        else:
            self.layoutImage = self.scenaryToLayout(PyQt5.QtGui.QPixmap(layout_filename))
        
        if start_pos is None:
            self.position = PyQt5.QtCore.QPoint(self.scenaryPix.width()/2, self.scenaryPix.height()/2)
        else:
            self.position = PyQt5.QtCore.QPoint(start_pos[0], start_pos[1])
        self.fixPosition()
            
        self.avatarWidth = 30;
        if avatar_filename is None:
            self.avatarPix = PyQt5.QtGui.QPixmap(self.avatarWidth, self.avatarWidth)
            self.avatarPix.fill(PyQt5.QtGui.QColor(255, 0, 0, 255))
        else:
            self.avatarPix = PyQt5.QtGui.QPixmap(avatar_filename)
  
        self.setWindowTitle('Welcome til Ellas og Vedranas labirint!')
          
        # Atributes relating to the transformation between widget 
        # coordinate system and image coordinate system
        self.zoomFactor = 1 # accounts for resizing of the widget and for zooming in the part of the image
        self.padding = PyQt5.QtCore.QPoint(0, 0) # padding when aspect ratio of image and widget does not match
        self.target = PyQt5.QtCore.QRect(0, 0, self.width(),self.height()) # part of the target being drawn on
        self.source = PyQt5.QtCore.QRect(0, 0, 
                self.scenaryPix.width(), self.scenaryPix.height()) # part of the image being drawn
        self.offset = PyQt5.QtCore.QPoint(0, 0) # offset between image center and area of interest center
       
        # Flags needed to keep track of different states
        self.newZoomValues = None
        
        # Label for displaying text overlay
        self.textField = PyQt5.QtWidgets.QLabel(self)
        self.textField.setStyleSheet("background-color: rgba(191,191,191,191)")
        self.textField.setTextFormat(PyQt5.QtCore.Qt.RichText)
        self.textField.resize(0,0)
        self.textField.move(10,10)     
        self.hPressed = False
        self.textField.setAttribute(PyQt5.QtCore.Qt.WA_TransparentForMouseEvents)
        #self.textField.setAttribute(PyQt5.QtCore.Qt.WA_TranslucentBackground) # considered making bacground translucent      
        
        self.spacePressed = False
        self.multiplier = 5
        
        # Timer for displaying text overlay
        self.timer = PyQt5.QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hideText)

        # Playtime
        initial_zoom = min(2000/max(self.scenaryPix.width(), 
                4*self.scenaryPix.height()/3),1) # downsize if larger than (2000,1500)
        self.resize(initial_zoom*self.scenaryPix.width(), 
                    initial_zoom*self.scenaryPix.height())
        self.show()
        
        self.showInfo(self.introText(),5000)
        print(self.introText(False))
            
    
    def fixPosition(self):
        pos_c = self.position.x()
        pos_r = self.layoutImage.shape[0] - self.position.y()
        distances = np.fromfunction(lambda r, c: abs(r-pos_r) + abs(c-pos_c), self.layoutImage.shape, dtype=int)
        p = np.unravel_index(np.argmax((np.max(distances)-distances)*(self.layoutImage==self.layoutItems['AIR'])), self.layoutImage.shape)
        self.position = PyQt5.QtCore.QPoint(p[1], p[0])
     
    helpText = (
        '<i>Hjælp for labirint</i> <br>' 
        '<b>DU SPILLER MEED TASERNE:</b> <br>' 
        '&nbsp; &nbsp; <b>piletaster</b> flytter din brik <br>')
    
    @classmethod
    def introText(cls, rich = True):
        if rich:
            s = '<i>Starter labirint.</i> <br> For hjælp, press <b>H</b>'
        else:
            s = "Starter labirint. For hjælp, press 'H'."
        return s
        
    def showHelp(self):
        self.timer.stop()
        self.showText(self.helpText)
    
    def showInfo(self, text, time=1000):
        if not self.hPressed:
            self.timer.start(time)
            self.showText(text)
    
    def showText(self, text):
        self.textField.setText(text)
        self.textField.adjustSize()
        self.update()
          
    def hideText(self):
        self.textField.resize(0,0)
        self.update()
        

    def paintEvent(self, event):
        """ Paint event for displaying the content of the widget."""
        painter_display = PyQt5.QtGui.QPainter(self) # this is painter used for display
        painter_display.setCompositionMode(
                    PyQt5.QtGui.QPainter.CompositionMode_SourceOver)
        painter_display.drawPixmap(self.target, self.scenaryPix, 
                                       self.source)
        painter_display.drawPixmap(self.avatarTarget(), self.avatarPix)
        
    def resizeEvent(self, event):
        """ Triggered by resizing of the widget window. """

 
        zoomWidth = self.width()/self.source.width()
        zoomHeight = self.height()/self.source.height() 
        
        # depending on aspect ratios, either pad up and down, or left and rigth
        if zoomWidth > zoomHeight:
            self.zoomFactor = zoomHeight
            self.padding = PyQt5.QtCore.QPoint((int(self.width() 
                            - self.source.width()*self.zoomFactor)/2), 0)
        else:
            self.zoomFactor = zoomWidth
            self.padding = PyQt5.QtCore.QPoint(0, int((self.height()
                            - self.source.height()*self.zoomFactor)/2))
            
        self.target = PyQt5.QtCore.QRect(self.padding, 
                            self.rect().bottomRight() - self.padding)
        
 
    def avatarTarget(self):
        
        return PyQt5.QtCore.QRect(
                self.padding.x() + self.position.x()*self.zoomFactor - self.avatarWidth/2*self.zoomFactor, 
                self.padding.y() + self.position.y()*self.zoomFactor - self.avatarWidth/2*self.zoomFactor, 
                self.avatarWidth*self.zoomFactor, self.avatarWidth*self.zoomFactor)
    
    def moveMore(self, direction):
        for i in range(self.multiplier):
            self.move(direction)                 
            
    def move(self, direction):
        
        if direction=='UP':
            if self.layoutImage[self.position.y()-1, self.position.x()] == self.layoutItems['AIR']:
                self.position.setY(self.position.y()-1)
            else:
                one = self.layoutImage[self.position.y()-1, self.position.x()-1] == self.layoutItems['AIR']
                other = self.layoutImage[self.position.y()-1, self.position.x()+1] == self.layoutItems['AIR']
                if one and not other:
                    self.position.setY(self.position.y()-1)
                    self.position.setX(self.position.x()-1)
                elif other and not one: 
                    self.position.setY(self.position.y()-1)
                    self.position.setX(self.position.x()+1)
        elif direction == 'DOWN':
            if self.layoutImage[self.position.y()+1, self.position.x()] == self.layoutItems['AIR']:
                self.position.setY(self.position.y()+1)
            else:
                one = self.layoutImage[self.position.y()+1, self.position.x()-1] == self.layoutItems['AIR']
                other = self.layoutImage[self.position.y()+1, self.position.x()+1] == self.layoutItems['AIR']
                if one and not other:
                    self.position.setY(self.position.y()+1)
                    self.position.setX(self.position.x()-1)
                elif other and not one: 
                    self.position.setY(self.position.y()+1)
                    self.position.setX(self.position.x()+1)
        elif direction == 'LEFT':
            if self.layoutImage[self.position.y(), self.position.x()-1] == self.layoutItems['AIR']:
                self.position.setX(self.position.x()-1)
            else:
                one = self.layoutImage[self.position.y()-1, self.position.x()-1] == self.layoutItems['AIR']
                other = self.layoutImage[self.position.y()+1, self.position.x()-1] == self.layoutItems['AIR']
                if one and not other:
                    self.position.setY(self.position.y()-1)
                    self.position.setX(self.position.x()-1)
                elif other and not one: 
                    self.position.setY(self.position.y()+1)
                    self.position.setX(self.position.x()-1)
        elif direction == 'RIGHT':
            if self.layoutImage[self.position.y(), self.position.x()+1] == self.layoutItems['AIR']:
                self.position.setX(self.position.x()+1)
            else:
                one = self.layoutImage[self.position.y()-1, self.position.x()+1] == self.layoutItems['AIR']
                other = self.layoutImage[self.position.y()+1, self.position.x()+1] == self.layoutItems['AIR']
                if one and not other:
                    self.position.setY(self.position.y()-1)
                    self.position.setX(self.position.x()+1)
                elif other and not one: 
                    self.position.setY(self.position.y()+1)
                    self.position.setX(self.position.x()+1)
     
    
    def keyPressEvent(self, event):
        if event.key()==32: # space
            if not self.spacePressed:
                self.spacePressed = True
                self.multiplier = 10
        if event.key()==16777235: # uparrow
            self.moveMore('UP')
            self.update()
        elif event.key()==16777237: # downarrow
            self.moveMore('DOWN')
            self.update()
        if event.key()==16777236: # rightarrow
            self.moveMore('RIGHT')
            self.update()
        elif event.key()==16777234: # leftarrow
            self.moveMore('LEFT')
            self.update()
        elif event.key()==72: # h        
            if not self.hPressed:
                self.hPressed = True
                self.showHelp()
        elif event.key()==16777216: # escape
            self.closeEvent(event)
        
    def keyReleaseEvent(self, event):
        if event.key()==72: # h
            self.hideText()
            self.hPressed = False
        elif event.key()==32: # space
            self.multiplier = 1
            self.spacePressed = False
            
    def closeEvent(self, event):
        self.showInfo("Bye, I'm closing")
        PyQt5.QtWidgets.QApplication.quit()
        # hint from: https://stackoverflow.com/questions/54045134/pyqt5-gui-cant-be-close-from-spyder
        # should also check: https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder
        
    colors = np.array([
        [0, 0, 0], # WALL
        [255, 255, 255]], # AIR
        dtype=np.uint8)

    layoutItems = {
        'AIR' : 1,
        'WALL' : 0}     

    # METHODS TRANSFORMING BETWEEN NUMPY (RGBA AND LABELS) AND QT5 DATA TYPES:
    @classmethod
    def rgbaToLabels(cls,rgba):
        """RGBA image to labels from 0 to N. Uses colors. All numpy."""    
        rgb = rgba.reshape(-1,4)[:,:3] # unfolding and removing alpha channel
        dist = np.sum(abs(rgb.reshape(-1,1,3).astype(np.int16) 
                - cls.colors.reshape(1,-1,3).astype(np.int16)), axis=2) # distances to pre-defined colors
        labels = np.empty((rgb.shape[0],), dtype=np.uint8)
        np.argmin(dist, axis=1, out=labels) # label given by the smallest distances
        labels = labels.reshape(rgba.shape[:2]) # folding back
        return(labels)
    
    @classmethod
    def labelsToRgba(cls, labels, opacity=1):
        """Labels from 0 to N to RGBA. Uses colors. All numpy."""
        rgb = cls.colors[labels,:]
        a = (255*opacity*(labels>0)).astype(np.uint8) # alpha channel
        a.shape = a.shape + (1,)
        rgba = np.concatenate((rgb, a), axis=2)
        return(rgba)
    
    @staticmethod
    def pixmapToArray(qpixmap):
        """Qt pixmap to np array. Assumes an 8-bit RGBA pixmap."""
        qimage = qpixmap.toImage().convertToFormat(PyQt5.QtGui.QImage.Format_RGBA8888)
        buffer = qimage.constBits()
        buffer.setsize(qpixmap.height() * qpixmap.width() * 4) # 4 layers for RGBA
        rgba = np.frombuffer(buffer, np.uint8).reshape((qpixmap.height(), 
                qpixmap.width(), 4))
        return rgba.copy()
    
    @staticmethod
    def rgbaToPixmap(rgba):
        """Np array to Qt pixmap. Assumes an 8-bit RGBA image."""
        rgba = rgba.copy()
        qimage = PyQt5.QtGui.QImage(rgba.data, rgba.shape[1], rgba.shape[0], 
                                    PyQt5.QtGui.QImage.Format_RGBA8888)
        qpixmap = PyQt5.QtGui.QPixmap(qimage)
        return qpixmap
    
    @staticmethod
    def grayToPixmap(gray):
        """Uint8 grayscale image to Qt pixmap via RGBA image."""
        rgba = np.tile(gray,(4,1,1)).transpose(1,2,0)
        rgba[:,:,3] = 255
        qpixmap = Labyrinth.rgbaToPixmap(rgba)
        return qpixmap
    
    @staticmethod
    def scenaryToLayout(qpixmap):
        rgba = Labyrinth.pixmapToArray(qpixmap)
        labels = Labyrinth.rgbaToLabels(rgba)
        return labels                     
      
if __name__ == '__main__':
          
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    if len(sys.argv)>1:
        filename = sys.argv[1]
        ex = Labyrinth(filename)
    else:
        ex = Labyrinth()
        ex = Labyrinth(scenary_filename='toppen_scenary.png', 
                       layout_filename='toppen_layout.png', 
                       avatar_filename='anders.jpg', 
                       start_pos = (960,1183))
    sys.exit(app.exec_())  
    
    
    
    