from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
from layer_canvas import LayerCanvas
from material_definitions import MATERIAL_DEFINITIONS


class SoundInsulationUI(QMainWindow):       # Main UI class for the application
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Insulation Performance")
        self.resize(400, 800)

        self.layers = []
        self.active_layer_index = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # groubox = panel, combobox = dropdwon menu

        # Layer section: panel for configuration and canvas
        self.layer_panel = QGroupBox("Layer Configuration & Visualization")
        self.layer_panel.setFixedHeight(300)
        layer_panel_layout = QVBoxLayout()
        self.layer_panel.setLayout(layer_panel_layout)
        main_layout.addWidget(self.layer_panel)

        # Layer input section: dropdown, thickness input, add button
        layer_config_layout = QHBoxLayout()
        self.layer_type_dropdown = QComboBox()
        self.layer_type_dropdown.addItems(["Select Material"] + list(MATERIAL_DEFINITIONS.keys()))

        self.layer_thickness_input = QLineEdit()
        self.layer_thickness_input.setPlaceholderText("Enter thickness [mm]")

        self.add_layer_button = QPushButton("Add Layer")
        self.add_layer_button.clicked.connect(self.add_layer)

        # Add input widgets to layout
        layer_config_layout.addWidget(self.layer_type_dropdown)
        layer_config_layout.addWidget(self.layer_thickness_input)
        layer_config_layout.addWidget(self.add_layer_button)
        layer_panel_layout.addLayout(layer_config_layout)

        # Image + Canvas display section
        top_visual_layout = QHBoxLayout()
        top_visual_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Load and display image if available
        image_path = os.path.join(os.path.dirname(__file__), "image.png")
        if os.path.exists(image_path):
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaledToHeight(100, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setFixedWidth(pixmap.width() + 20)
            top_visual_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Create canvas widget for drawing layers
        self.canvas = LayerCanvas(self.layers, self.on_layer_selected, self.get_active_layer_index)
        top_visual_layout.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignVCenter)
        layer_panel_layout.addLayout(top_visual_layout)

        # Layer management buttons: delete or clear all
        control_buttons_layout = QHBoxLayout()
        self.delete_layer_button = QPushButton("Delete Selected")
        self.delete_layer_button.clicked.connect(self.delete_selected_layer)

        self.clear_layers_button = QPushButton("Clear All")
        self.clear_layers_button.clicked.connect(self.clear_all_layers)

        control_buttons_layout.addWidget(self.delete_layer_button)
        control_buttons_layout.addWidget(self.clear_layers_button)
        layer_panel_layout.addLayout(control_buttons_layout)

        # Panel for displaying and editing material properties
        self.property_panel = QGroupBox("Material Properties")
        self.property_layout = QVBoxLayout()
        self.property_panel.setLayout(self.property_layout)
        main_layout.addWidget(self.property_panel)

    # Return the currently selected layer index
    def get_active_layer_index(self):
        return self.active_layer_index

    # Handle adding a new layer
    def add_layer(self):
        material_type = self.layer_type_dropdown.currentText()
        thickness = self.layer_thickness_input.text()

        # Validate input
        if material_type == "Select Material" or not thickness:
            return

        thickness_val = float(thickness)

        # Create layer dictionary
        layer_info = {
            "type": material_type,
            "thickness": thickness_val,
            "widget": None,
            "fields": [],
            "metadata": []
        }

        self.layers.append(layer_info)                          # Add to internal list
        self.canvas.repaint()                                   # Trigger re-draw

    # Delete the currently selected layer
    def delete_selected_layer(self):
        if self.active_layer_index is not None and 0 <= self.active_layer_index < len(self.layers):
            self.layers.pop(self.active_layer_index)
            self.active_layer_index = None
            self.canvas.repaint()
            self.clear_property_panel()

    # Remove all layers
    def clear_all_layers(self):
        self.layers.clear()
        self.active_layer_index = None
        self.canvas.repaint()
        self.clear_property_panel()

    # Clear all widgets from the property panel
    def clear_property_panel(self):
        for i in reversed(range(self.property_layout.count())):
            widget = self.property_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

    # Called when a layer is selected from the canvas
    def on_layer_selected(self, index):
        self.active_layer_index = index
        layer = self.layers[index]
        material_type = layer["type"]

        self.clear_property_panel()
        layer["fields"] = []
        layer["metadata"] = []

        # Dynamically create input fields based on material definition
        for prop in MATERIAL_DEFINITIONS[material_type]["properties"]:
            label = QLabel(prop["label"])
            field = QLineEdit()

            if prop["name"] == "thickness":
                field.setText(str(layer["thickness"]))
                field.setReadOnly(True)

            self.property_layout.addWidget(label)
            self.property_layout.addWidget(field)

            layer["fields"].append((label, field))
            layer["metadata"].append((prop["name"], prop["label"], field))

        self.canvas.repaint()                                   # Highlight the selected layer