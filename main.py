#!/usr/bin/python -W ignore::DeprecationWarning
import sys

import os
import glob
import random
import cv2
import numpy as np
import datetime

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from node import *
from edge import *

qtCreatorFile = "mainwindow.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, argv):

        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # graph stuff
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.view = self.graphicsView
        self.view.setRenderHint(QPainter.Antialiasing)

        self.newnodeidx = 0
        self.newedgeidx = 0
        self.newconnectionidx = 0

        self.isConnecting = False

        # FIXME: remove in production version
        self.insertTestStuff() # insert some test nodes and connections

        self.view.show()


    def scaleView(self, scaleFac) :
        factor = self.view.matrix().scale(scaleFac, scaleFac).mapRect(QRectF(0, 0, 1, 1)).width();
        if (factor < 0.07 or factor > 100):
             return
        self.view.scale(scaleFac, scaleFac)
          
    def wheelEvent(self, event):
        self.scaleView(pow(2., -event.delta() / 240.0));


    def insertTestStuff(self):
        # add a node
        self.nodes = {}
        self.edges = []
        self.connections = {}

        # sample nodes, objects + processes
        idx_v = self.addNode(0,0,'object', 'Video')
        idx_t = self.addNode(150,0,'process', 'Threshold')
        idx_m = self.addNode(300,0,'object', 'Map')


        # sample connections
        # FIXME: need to encode types of edges (related to semantics of OPM)
        self.connectNodes(idx_v, idx_t, 'hollow-arrow')
        self.connectNodes(idx_t, idx_m, 'filled-arrow')

        self.updatePaths()


    def updateNodes(self):
        model = QStandardItemModel(self.list_overview_nodes)
        for key in self.nodes:
            # add node to list_overview_nodes
            item = QStandardItem(self.nodes[key].name)
            model.appendRow(item)
        self.list_overview_nodes.setModel(model)
        self.list_overview_nodes.show()


    def btn_add_clicked(self):
        '''
        button to add nodes manually
        '''
        # get text for node
        name = self.text_node.toPlainText()
        if self.radio_obj.isChecked() or self.radio_proc.isChecked():
            if self.radio_obj.isChecked():
                type = 'object'
            else:
                type = 'process'
            self.addNode(0,0,type,name)
        else:
            print "Error: please check a radio-box to select type!"


    def connect(self, index):
        '''
        called from a node if its connect function is triggered,
        makes connection if second node's connect function is triggered
        '''
        if self.isConnecting == False:
            self.firstNode = index
            self.isConnecting = True
        else:
            self.connectNodes(self.firstNode, index, 'hollow-circle')
            print "Connected !"
            self.isConnecting = False

    def connectNodes(self, idx_node1, idx_node2, edgetype, tag=""):
        self.connections[self.newconnectionidx] = {}
        self.connections[self.newconnectionidx]["indices"] = [idx_node1, idx_node2]
        self.connections[self.newconnectionidx]["edgetype"] = edgetype
        self.connections[self.newconnectionidx]["tag"] = tag
        self.newconnectionidx += 1
        self.updatePaths()

    def removeConnection(self, idx_connection):
        '''
        find the connection with right pathid, and remove it from the dict
        '''
        del self.connections[idx_connection]
        self.updatePaths()

    def updatePaths(self):
        '''
        redraws edges
        - if any of the nodes is moved
        - if connections are added or deleted
        '''
        # clear existing edges from scene
        for key in self.edges:
            self.scene.removeItem(self.edges[key])

        model = QStandardItemModel(self.list_overview_connections)
        # add fresh edges between nodes
        self.edges = {}
        for key in self.connections:
            c = self.connections[key]["indices"]

            item = QStandardItem(self.nodes[c[0]].name + " -> " + self.nodes[c[1]].name)
            model.appendRow(item)

            pos = self.nodes[c[0]].pos()
            npos = self.nodes[c[1]].pos()

            start_x = pos.x()
            end_x = npos.x() 

            start_y = pos.y()
            end_y = npos.y() 

            if npos.x() > pos.x():
                start_x = pos.x() + self.nodes[c[0]].boundingRect().width() 
                end_x = npos.x() 
            elif npos.x() < pos.x():
                start_x = pos.x() 
                end_x = npos.x() + self.nodes[c[1]].boundingRect().width() 

            start_y = pos.y() + self.nodes[c[0]].boundingRect().height() / 2
            end_y = npos.y() + self.nodes[c[1]].boundingRect().height() / 2

            p1 = Edge(QPointF(start_x, start_y), QPointF(end_x,end_y), self, key, self.connections[key]["edgetype"], self.connections[key]["tag"])
            self.edges[key] = p1
            self.scene.addItem(p1)

        self.scene.update()

        self.list_overview_connections.setModel(model)
        self.list_overview_connections.show()


    def addNode(self,x,y,type,name):
        node = Node(self.newnodeidx, name, type, self)
        node.setPos(x,y)
        self.scene.addItem(node)
        self.nodes[self.newnodeidx] = node
        self.scene.update()
        self.updateNodes()

        self.newnodeidx += 1
        return self.newnodeidx-1 # return id of inserted node


    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        if e.key() == QtCore.Qt.Key_F:
            self.fwd_clicked()
        if e.key() == QtCore.Qt.Key_B:
            self.bwd_clicked()
        if e.key() == QtCore.Qt.Key_P:
            if self.play == False:
                self.timer.setInterval(1)
                self.timer.timeout.connect(self.fwd_clicked)
                self.timer.start()
                self.play = True
            else:
                self.timer.stop()
                self.play = False


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp(sys.argv)
    window.show()
    sys.exit(app.exec_())
