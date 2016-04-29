from PyQt4.QtGui import *
from PyQt4.QtCore import *
import math

class Edge(QGraphicsItem):
    Pi = math.pi
    TwoPi = 2.0 * Pi

    Type = QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode, parent, index, type, tag=""):
        super(Edge, self).__init__()

        self.arrowSize = 10.0
        self.sourcePoint = QPointF()
        self.destPoint = QPointF()
        self.type = type
        self.tag = tag

        #self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(True)
        self.source = sourceNode
        self.dest = destNode
        self.adjust()

        self.parent = parent
        self.index = index
        self.hover = False

    def hoverEnterEvent(self, event):
        self.hover = True
        print "Hover hover!"

    def hoverLeaveEvent(self, event):
        self.hover = False
        print "No no hover"


    def showDialog(self):
        text, ok = QInputDialog.getText(self.parent, "QInputDialog.getText()","Tag:", QLineEdit.Normal, "")
        if ok:
            self.parent.connections[self.index]["tag"] = text
            self.tag = text

    def contextMenuEvent(self,event):
        # FIXME: need to encode types of edges (related to semantics of OPM)
        actions = ["delete", "tag", "filled-arrow", "hollow-arrow", "structural", "bi-directional", "hollow-circle"]
        menu = QMenu()
        for a in actions:
            menu.addAction(a)

        a = menu.exec_(event.screenPos())

        idx = actions.index(a.text())
        if idx == 0: # delete
            print "Removing"
            self.parent.removeConnection(self.index)
        elif idx == 1: # tag
            print "Tagging"
            self.showDialog()
        else:
            self.type = actions[idx]
            self.parent.connections[self.index]["edgetype"] = actions[idx]
            self.parent.updatePaths()

    def type(self):
        return Edge.Type

    def sourceNode(self):
        return self.source

    def setSourceNode(self, node):
        self.source = node
        self.adjust()

    def destNode(self):
        return self.dest

    def setDestNode(self, node):
        self.dest = node
        self.adjust()

    def adjust(self):
        if not self.source or not self.dest:
            return

        line = QLineF(self.source, self.dest)
        length = line.length()

        self.prepareGeometryChange()

        if length > 20.0:
            edgeOffset = QPointF((line.dx() * 10) / length,
                    (line.dy() * 10) / length)

            self.sourcePoint = line.p1() + edgeOffset
            self.destPoint = line.p2() - edgeOffset
        else:
            self.sourcePoint = line.p1()
            self.destPoint = line.p1()

    def boundingRect(self):
        if not self.source or not self.dest:
            return QRectF()

        penWidth = 1.0
        extra = (penWidth + self.arrowSize) / 2.0

        return QRectF(self.sourcePoint,
                QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                        self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        if not self.source or not self.dest:
            return

        # Draw the line itself.
        line = QLineF(self.sourcePoint, self.destPoint)

        if line.length() == 0.0:
            return

        if not self.hover:
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        else:
            painter.setPen(QPen(Qt.red, 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(line)

        # Draw the arrows if there's enough room.
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = Edge.TwoPi - angle

        if self.type == 'hollow-arrow':
            destArrowP1 = self.destPoint + QPointF(math.sin(angle - Edge.Pi / 3) * self.arrowSize, math.cos(angle - Edge.Pi / 3) * self.arrowSize)
            destArrowP2 = self.destPoint + QPointF(math.sin(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize, math.cos(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize)
            painter.setBrush(Qt.white)
            painter.drawPolygon(QPolygonF([line.p2(), destArrowP1, destArrowP2]))
        elif self.type == 'filled-arrow':
            destArrowP1 = self.destPoint + QPointF(math.sin(angle - Edge.Pi / 3) * self.arrowSize, math.cos(angle - Edge.Pi / 3) * self.arrowSize)
            destArrowP2 = self.destPoint + QPointF(math.sin(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize, math.cos(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize)
            painter.setBrush(Qt.black)
            painter.drawPolygon(QPolygonF([line.p2(), destArrowP1, destArrowP2]))
        elif self.type == 'null-structural':
            destArrowP1 = self.destPoint + QPointF(math.sin(angle - Edge.Pi / 3) * self.arrowSize, math.cos(angle - Edge.Pi / 3) * self.arrowSize)
            destArrowP2 = self.destPoint + QPointF(math.sin(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize, math.cos(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize)
            painter.setBrush(Qt.white)
            painter.drawLine(QLineF(line.p2(), destArrowP1))
            painter.drawLine(QLineF(line.p2(), destArrowP2))
        elif self.type == 'bi-directional':
            destArrowP1 = self.destPoint + QPointF(math.sin(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize, math.cos(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize)
            destArrowP2 = self.sourcePoint + QPointF(math.sin(angle + Edge.Pi/3) * self.arrowSize, math.cos(angle + Edge.Pi/3) * self.arrowSize)

            painter.setBrush(Qt.white)
            painter.drawLine(QLineF(line.p2(), destArrowP1))
            painter.drawLine(QLineF(line.p1(), destArrowP2))

        elif self.type == 'hollow-circle':
            painter.setBrush(Qt.white)
            painter.drawEllipse(self.destPoint, 5, 5);

        if self.tag != "":
            painter.drawText(self.boundingRect().x() + self.boundingRect().width()/2. , self.boundingRect().y() + self.boundingRect().height()/2., self.tag)

        self.parent.scene.update()

