from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QScrollArea, QSpacerItem, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt
import sys


class SoundInsulationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Insulation Performance")
        self.setGeometry(100, 100, 800, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # --- Create Material Information Panel ---
        self.material_info_panel = QGroupBox("Material Information")
        material_info_layout = QVBoxLayout()
        self.material_info_panel.setLayout(material_info_layout)
        main_layout.addWidget(self.material_info_panel)

        # --- Material Type Selection Panel ---
        self.material_type_panel = QGroupBox("Material Type Selection")
        self.material_type_panel.setFixedSize(250, 200)
        material_layout = QVBoxLayout()

        # Material 1
        label1 = QLabel("Material 1:")
        self.material_dropdown1 = QComboBox()
        self.material_dropdown1.addItems(["Select Material", "Foam", "Aluminum"])

        # Material 2
        label2 = QLabel("Material 2:")
        self.material_dropdown2 = QComboBox()
        self.material_dropdown2.addItems(["Select Material", "Foam", "Aluminum"])

        # Material 3
        label3 = QLabel("Material 3:")
        self.material_dropdown3 = QComboBox()
        self.material_dropdown3.addItems(["Select Material", "Foam", "Aluminum"])

        self.material_dropdown1.currentTextChanged.connect(self.on_material_changed)
        self.material_dropdown2.currentTextChanged.connect(self.on_material_changed)
        self.material_dropdown3.currentTextChanged.connect(self.on_material_changed)

        material_layout.addWidget(label1)
        material_layout.addWidget(self.material_dropdown1)
        material_layout.addSpacing(10)
        material_layout.addWidget(label2)
        material_layout.addWidget(self.material_dropdown2)
        material_layout.addSpacing(10)
        material_layout.addWidget(label3)
        material_layout.addWidget(self.material_dropdown3)

        self.material_type_panel.setLayout(material_layout)
        material_info_layout.addWidget(self.material_type_panel)

        # --- Bottom Layout (Material Input Panel + Actions) ---
        bottom_layout = QHBoxLayout()
        material_info_layout.addLayout(bottom_layout)

        # --- Material Input Panel ---
        self.material_input_panel = QGroupBox("Material Input Panel")
        self.material_input_panel.setMinimumSize(600, 500)
        material_input_layout = QVBoxLayout()
        self.material_input_panel.setLayout(material_input_layout)
        bottom_layout.addWidget(self.material_input_panel)

        # --- Inner Scroll Area (Inside Material Input Panel) ---
        self.inner_scroll_area = QScrollArea()
        self.inner_scroll_area.setWidgetResizable(True)
        material_input_layout.addWidget(self.inner_scroll_area)

        # --- Properties Container (Holds Material Properties Panels) ---
        self.properties_container = QWidget()
        self.properties_layout = QVBoxLayout()
        self.properties_container.setLayout(self.properties_layout)
        self.inner_scroll_area.setWidget(self.properties_container)

        # --- Define Material Labels ---
        self.labels_foam = [
            "Thickness \n [m]", "Viscous CL \n [m]", "Thermal CL \n [m]", "Density \n [kg/m3]",
            "Airflow resistivity \n [Pa*s/m2]", "Tortuosity \n", "Porosity \n",
            "Loss Factor \n", "Poisson's Ratio \n "]  # Density와 Airflow resistivity를 왼쪽으로 이동

        self.labels_aluminum = [
            "Loss Factor", "Static Young's Modulus [Pa]", "Poisson's Ratio",
            "Density [kg/m3]", "Thickness [m]"]

        # --- Material Properties 1 ---
        self.property_panel_1 = QGroupBox("Material Properties 1")
        property_layout_1 = QGridLayout()
        self.property_panel_1.setLayout(property_layout_1)
        self.properties_layout.addWidget(self.property_panel_1)

        self.fields_panel_1 = []
        for label_text in self.labels_foam:
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            field = QLineEdit()
            self.fields_panel_1.append((label, field))

        # --- Material Properties 2 ---
        self.property_panel_2 = QGroupBox("Material Properties 2")
        property_layout_2 = QGridLayout()
        self.property_panel_2.setLayout(property_layout_2)
        self.properties_layout.addWidget(self.property_panel_2)

        self.fields_panel_2 = []
        for label_text in self.labels_foam:
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            field = QLineEdit()
            self.fields_panel_2.append((label, field))

        # --- Material Properties 3 ---
        self.property_panel_3 = QGroupBox("Material Properties 3")
        property_layout_3 = QGridLayout()
        self.property_panel_3.setLayout(property_layout_3)
        self.properties_layout.addWidget(self.property_panel_3)

        self.fields_panel_3 = []
        for label_text in self.labels_foam:
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            field = QLineEdit()
            self.fields_panel_3.append((label, field))

        # --- Calculation Panel ---
        self.calculation_panel = QGroupBox("Calculation")
        calculation_layout = QVBoxLayout()
        self.calculation_panel.setLayout(calculation_layout)
        main_layout.addWidget(self.calculation_panel)

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.perform_calculation)
        calculation_layout.addWidget(self.calculate_button)

        self.on_material_changed()

    def perform_calculation(self):
        print("Calculating...")

    def on_material_changed(self):
        """ Updates the displayed material properties based on dropdown selection. """
        selected1 = self.material_dropdown1.currentText()
        selected2 = self.material_dropdown2.currentText()
        selected3 = self.material_dropdown3.currentText()

        def update_panel(panel, layout, fields, labels, left_count, right_count):
            """ Update a panel layout to distribute properties into left and right columns. """
            # Hide all fields initially
            for label, field in fields:
                label.hide()
                field.hide()

            # Show and place left-side fields
            for i in range(left_count):
                fields[i][0].show()
                fields[i][1].show()
                layout.addWidget(fields[i][0], i, 0)
                layout.addWidget(fields[i][1], i, 1)

            # Show and place right-side fields
            for i in range(right_count):
                fields[i + left_count][0].show()
                fields[i + left_count][1].show()
                layout.addWidget(fields[i + left_count][0], i, 2)
                layout.addWidget(fields[i + left_count][1], i, 3)

            layout.update()  # Refresh layout

        # Material 1
        if selected1 == "Select Material":
            self.property_panel_1.hide()
        else:
            self.property_panel_1.show()
            for label, field in self.fields_panel_1:
                label.show()
                field.show()
            if selected1 == "Foam":
                update_panel(self.property_panel_1, self.property_panel_1.layout(), self.fields_panel_1,
                             self.labels_foam, 5, 4)  # Foam 순서 반영
            else:
                update_panel(self.property_panel_1, self.property_panel_1.layout(), self.fields_panel_1,
                             self.labels_aluminum, 3, 2)

        # Material 2
        if selected2 == "Select Material":
            self.property_panel_2.hide()
        else:
            self.property_panel_2.show()
            for label, field in self.fields_panel_2:
                label.show()
                field.show()
            if selected2 == "Foam":
                update_panel(self.property_panel_2, self.property_panel_2.layout(), self.fields_panel_2,
                             self.labels_foam, 5, 4)  # Foam 순서 반영
            else:
                update_panel(self.property_panel_2, self.property_panel_2.layout(), self.fields_panel_2,
                             self.labels_aluminum, 3, 2)

        # Material 3
        if selected3 == "Select Material":
            self.property_panel_3.hide()
        else:
            self.property_panel_3.show()
            for label, field in self.fields_panel_3:
                label.show()
                field.show()
            if selected3 == "Foam":
                update_panel(self.property_panel_3, self.property_panel_3.layout(), self.fields_panel_3,
                             self.labels_foam, 5, 4)  # Foam 순서 반영
            else:
                update_panel(self.property_panel_3, self.property_panel_3.layout(), self.fields_panel_3,
                             self.labels_aluminum, 3, 2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoundInsulationUI()
    window.show()
    sys.exit(app.exec())