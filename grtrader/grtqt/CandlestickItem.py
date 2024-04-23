import pyqtgraph as pg
from pyqtgraph import QtGui, QtCore


class QuotaItem(pg.GraphicsObject):
    # data's np.array list
    def __init__(self, data, color=None):
        pg.GraphicsObject.__init__(self)
        self.data = data
        if color is None:
            color = ['w' for x in range(len(data))]
        self.color = color
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        pg.setConfigOptions(leftButtonPan=False, antialias=False)
        for line_i in range(len(self.data)):
            lines = GetQuotaLines(self.data[line_i])
            p.setPen(pg.mkPen(self.color[line_i]))
            p.drawLines(*tuple(lines))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())
class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        pg.setConfigOptions(leftButtonPan=False, antialias=False)
        w = 0.25
        p.setPen(pg.mkPen('w'))
        p.setBrush(pg.mkBrush('w'))

        ma5_lines = GetQuotaLines(quota.MA(self.data['close']))
        p.drawLines(*tuple(ma5_lines))
        p.setPen(pg.mkPen('y'))
        ma10_lines = GetQuotaLines(quota.MA(self.data['close'], 10))
        p.drawLines(*tuple(ma10_lines))
        p.setPen(pg.mkPen(color_table['pink']))
        ma20_lines = GetQuotaLines(quota.MA(self.data['close'], 20))
        p.drawLines(*tuple(ma20_lines))
        # for (i, open, close, min, max) in self.data:
        for i in range(len(self.data['open'])):
            open, close, max, min = self.data['open'][i], self.data['close'][i], self.data['high'][i], self.data['low'][
                i]
            if open > close:
                p.setPen(pg.mkPen(color_table['line_desc']))
                p.setBrush(pg.mkBrush(color_table['line_desc']))
                p.drawLine(QtCore.QPointF(i, min), QtCore.QPointF(i, max))
                p.drawRect(QtCore.QRectF(i - w, open, w * 2, close - open))

            else:
                p.setPen(pg.mkPen('r'))
                if (max != close):
                    p.drawLine(QtCore.QPointF(i, max), QtCore.QPointF(i, close))
                if (min != open):
                    p.drawLine(QtCore.QPointF(i, open), QtCore.QPointF(i, min))
                if (close == open):
                    p.drawLine(QtCore.QPointF(i - w, open), QtCore.QPointF(i + w, open))
                else:
                    p.drawLines(QtCore.QLineF(QtCore.QPointF(i - w, close), QtCore.QPointF(i - w, open)),
                                QtCore.QLineF(QtCore.QPointF(i - w, open), QtCore.QPointF(i + w, open)),
                                QtCore.QLineF(QtCore.QPointF(i + w, open), QtCore.QPointF(i + w, close)),
                                QtCore.QLineF(QtCore.QPointF(i + w, close), QtCore.QPointF(i - w, close)))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())