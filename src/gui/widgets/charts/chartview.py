from PySide6.QtCharts import QChartView
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import (
    QClipboard, QCursor, QPainter
)
from PySide6.QtWidgets import QSizePolicy

class GudPyChartView(QChartView):
    """
    Class to represent a GudPyChartView. Inherits QChartView.

    ...
    Attributes
    ----------
    chart : GudPyChart
        Chart to be shown in the view.
    Methods
    -------
    wheelEvent(event):
        Event handler for using the scroll wheel.
    toggleLogarithmicAxes():
        Toggles logarithmic axes in the chart.
    contextMenuEvent(event):
        Creates context menu.
    keyPressEvent(event):
        Handles key presses.
    enterEvent(event):
        Handles the mouse entering the chart view.
    leaveEvent(event):
        Handles the mouse leaving the chart view.
    """
    def __init__(self, parent):
        """
        Constructs all the necessary attributes for the GudPyChartView object.
        Calls super()._init__ which calls the dunder init method
        from QChartView.
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget.
        """
        super(GudPyChartView, self).__init__(parent=parent)

        # Set size policy.
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        )

        # Enable rectangualar rubber banding.
        self.setRubberBand(QChartView.RectangleRubberBand)

        # Enable Antialiasing.
        self.setRenderHint(QPainter.Antialiasing)
        self.clipboard = QClipboard(self.parent())

        self.previousPos = 0

    def wheelEvent(self, event):
        """
        Event handler called when the scroll wheel is used.
        This event is overridden for zooming in/out.
        Parameters
        ----------
        event : QWheelEvent
            Event that triggered the function call.
        """
        # Decide on the zoom factor.
        # If y > 0, zoom in, if y < 0 zoom out.
        zoomFactor = 2.0 if event.angleDelta().y() > 0 else 0.5

        # Create QRect area to zoom in on.
        chartArea = self.chart().plotArea()
        left = chartArea.left()
        top = chartArea.top()
        width = chartArea.width() / zoomFactor
        height = chartArea.height() / zoomFactor
        zoomArea = QRectF(left, top, width, height)

        # Move the rectangle to the mouse position.
        mousePos = self.mapFromGlobal(QCursor.pos())
        zoomArea.moveCenter(mousePos)

        # Zoom in on the area.
        self.chart().zoomIn(zoomArea)

        # Scroll to match the zoom.
        delta = self.chart().plotArea().center() - mousePos
        self.chart().scroll(delta.x(), -delta.y())

        self.zoomArea = zoomArea
        self.scrolled = (delta.x(), -delta.y())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.MiddleButton:

            if self.previousPos:
                offset = event.pos() - self.previousPos
            else:
                offset = event.pos()
            self.chart().scroll(-offset.x(), offset.y())

            self.previousPos = event.pos()
            event.accept()
        return super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.previousPos = event.pos()
        return super().mousePressEvent(event)

    def copyPlot(self):
        pixMap = self.grab()
        self.clipboard.setPixmap(pixMap)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            event.accept()
        else:
            return super(GudPyChartView, self).mouseReleaseEvent(event)

    def enterEvent(self, event):
        """
        Handles the mouse entering the chart view.
        Gives focus to the chart view.
        """
        # Acquire focus.
        self.setFocus(Qt.OtherFocusReason)
        return super().enterEvent(event)

    def leaveEvent(self, event):
        """
        Handles the mouse leaving the chart view.
        Gives focus back to the parent.
        """
        # Relinquish focus.
        self.parent().setFocus(Qt.OtherFocusReason)
        return super().leaveEvent(event)