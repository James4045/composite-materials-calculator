from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt6.QtCore import QRect, Qt
import os

from material_definitions import MATERIAL_DEFINITIONS

class LayerCanvas(QWidget):  # Custom QWidget for rendering layered materials
    def __init__(self, layers, on_click_callback, get_active_index):
        super().__init__()
        self.layers = layers
        self.on_click_callback = on_click_callback
        self.get_active_index = get_active_index

        self.setMinimumHeight(120)
        self.layer_rects = []

        # Load image once
        image_path = os.path.join(os.path.dirname(__file__), "image.png")
        self.pixmap = QPixmap(image_path) if os.path.exists(image_path) else None

    def paintEvent(self, event):
        painter = QPainter(self)
        canvas_width = self.width()

        # --- 이미지 렌더링 (좌측에 고정) ---
        image_margin = 10
        image_width = 100
        if self.pixmap:
            scaled_pixmap = self.pixmap.scaledToWidth(image_width, Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(image_margin, 10, scaled_pixmap)
        image_offset = image_width + image_margin * 2 if self.pixmap else 0

        # --- 레이어 시각화 ---
        SCALE = 3
        total_width = sum(int(float(layer.get("thickness", 0) or 0) * SCALE) for layer in self.layers)
        x_offset = image_offset + max((canvas_width - image_offset - total_width) // 2, 0)

        self.layer_rects = []
        for i, layer in enumerate(self.layers):
            thickness = float(layer.get("thickness", 0) or 0)

            # --- 조건에 따라 스케일 설정 ---
            if thickness <= 10:
                scale = -2/3*(thickness-1)+8
            else:
                scale = 2
            width = int(thickness * scale)

            material_type = layer.get("type", "")
            definition = MATERIAL_DEFINITIONS.get(material_type)
            material_color = definition.get("color", "gray")
            color = QColor(material_color)

            rect = QRect(x_offset, 10, width, 100)
            self.layer_rects.append(rect)
            painter.setBrush(color)

            active_index = self.get_active_index()
            pen = QPen(Qt.GlobalColor.red, 3) if i == active_index else QPen(Qt.GlobalColor.black, 1)
            painter.setPen(pen)
            painter.drawRect(rect)
            x_offset += width

    def mousePressEvent(self, event):  # Handle mouse click events to detect layer selection
        pos = event.position().toPoint()
        for i, rect in enumerate(self.layer_rects):
            if rect.contains(pos):
                self.on_click_callback(i)
                break