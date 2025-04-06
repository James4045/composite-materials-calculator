from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import QRect, Qt
from material_definitions import MATERIAL_DEFINITIONS

class LayerCanvas(QWidget):         # Custom QWidget for rendering layered materials
    def __init__(self, layers, on_click_callback, get_active_index):
        super().__init__()
        self.layers = layers
        self.on_click_callback = on_click_callback
        self.get_active_index = get_active_index

        self.setMinimumHeight(120)
        self.layer_rects = []

    def paintEvent(self, event):    # Handles the drawing of layer rectangles
        painter = QPainter(self)
        canvas_width = self.width()
        SCALE = 3
        total_width = sum(int(float(layer.get("thickness", 0) or 0) * SCALE) for layer in self.layers)
        x_offset = (canvas_width - total_width) // 2 if total_width < canvas_width else 0
        self.layer_rects = []

        # enumerate(): binds indexes and elements into tuples
        # dict.get("{key}", default) : getting values for keys in dictionary, default value can be specified
        # A or B : return A or B, A priority

        for i, layer in enumerate(self.layers):
            thickness = float(layer.get("thickness", 0) or 0)
            width = int(thickness * SCALE)

            material_type = layer.get("type", "")
            definition = MATERIAL_DEFINITIONS.get(material_type)
            material_color = definition.get("color", "gray")
            color = QColor(material_color)

            # QRect(x,y,width,height), (x,y) = start point
            # setBrush : specify fill color
            # setPen : specify border color

            rect = QRect(x_offset, 10, width, 100)
            self.layer_rects.append(rect)
            painter.setBrush(color)

            active_index = self.get_active_index()                      # Get the currently selected layer index
            pen = QPen(Qt.GlobalColor.red, 3) if i == active_index else QPen(Qt.GlobalColor.black, 1)

            painter.setPen(pen)
            painter.drawRect(rect)
            x_offset += width

    def mousePressEvent(self, event):   # Handle mouse click events to detect layer selection
        pos = event.position().toPoint()                                # Get mouse click position as QPoint
        for i, rect in enumerate(self.layer_rects):
            if rect.contains(pos):
                self.on_click_callback(i)
                break