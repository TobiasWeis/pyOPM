#!/usr/bin/env python
# coding: utf-8

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import math

class Node(QGraphicsTextItem):
        def __init__(self, index, name, type, parent):
                super(Node, self).__init__(name + "(%d)" % index)
                self.index = index
                self.parent = parent
                #self.cb = cb
                self.name = name
                self.type = type

                self.setZValue(1)
                self.setFlag(QGraphicsItem.ItemIsMovable)
                self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
                        

        '''
        def mousePressEvent(self, event):
            if event.button() == 2: # right mouse button
                print "Initiating connection"
            else:
                event.ignore()

        '''

        def contextMenuEvent(self, event):
            print "Initializing connection!"
            self.parent.connect(self.index)
                
        def paint(self,painter,option,widget):
            p = QPen(QBrush(QColor("#0000ff")), 1, Qt.DashLine)
            painter.setPen(p)
            if self.type == 'object':
                    painter.drawRoundedRect(self.boundingRect().x(),self.boundingRect().y(),self.boundingRect().width(),self.boundingRect().height(), 2,2)
            elif self.type == 'process':
                painter.drawEllipse(self.boundingRect().x(),self.boundingRect().y(),self.boundingRect().width(),self.boundingRect().height())

            p = QPen(QBrush(QColor("#000000")), 4, Qt.DashLine)
            painter.setPen(p)
            #painter.drawText(self.boundingRect(), 0, self.name)
            painter.drawText(self.boundingRect().x() , self.boundingRect().y() + self.boundingRect().height()/2., self.name + "(%d)"%(self.index))

               
        def itemChange(self, change, value):
            if change == QGraphicsItem.ItemPositionChange:
                    self.parent.updatePaths()
            return QGraphicsTextItem.itemChange(self, change, value)




