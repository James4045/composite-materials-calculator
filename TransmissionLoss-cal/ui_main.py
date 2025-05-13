import os
import sys
import numpy as np
import json
import copy
import pandas as pd
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox, QSizePolicy, QFileDialog, QDialog,
    QScrollArea, QTableWidget, QTableWidgetItem, QTabWidget, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
from layer_canvas import LayerCanvas
from material_definitions import MATERIAL_DEFINITIONS

calculate_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "calculate"))
if calculate_path not in sys.path:
    sys.path.append(calculate_path)
from calculation import run_simulation_from_ui


class AxisRangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Set Axis Range")
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.x_label = QLabel("X Axis Range:")
        self.xmin_input = QLineEdit()
        self.xmax_input = QLineEdit()
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("From:"))
        x_layout.addWidget(self.xmin_input)
        x_layout.addWidget(QLabel("To:"))
        x_layout.addWidget(self.xmax_input)

        layout.addWidget(self.x_label)
        layout.addLayout(x_layout)

        self.y_label = QLabel("Y Axis Range:")
        self.ymin_input = QLineEdit()
        self.ymax_input = QLineEdit()
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("From:"))
        y_layout.addWidget(self.ymin_input)
        y_layout.addWidget(QLabel("To:"))
        y_layout.addWidget(self.ymax_input)

        layout.addWidget(self.y_label)
        layout.addLayout(y_layout)

        # --- OK, Cancel 버튼 구성 ---
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.accept)  # Qdialog 클래스에서 ok 시 사용하는 method (창 닫기 + 결과 반환)
        self.cancel_button.clicked.connect(self.reject)  # Qdialog 클래스에서 cancel 시 사용하는 method (창 닫기 + 결과 무시)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)


class ManageLegendDialog(QDialog):
    def __init__(self, graph_info_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Graph Info")
        self.resize(700, 400)
        self.graph_info_list = graph_info_list

        layout = QVBoxLayout()
        self.table = QTableWidget(len(graph_info_list), 4)
        self.table.setHorizontalHeaderLabels(["Graph Name", "Material Info", "File Name", "File Path"])

        for row, info in enumerate(graph_info_list):
            legend_item = QTableWidgetItem(info.get("legend", ""))
            material_item = QTableWidgetItem(info.get("material_info", "-"))
            file_name_item = QTableWidgetItem(os.path.basename(info.get("file_path", "-")))
            file_path_item = QTableWidgetItem(info.get("file_path", "-"))

            self.table.setItem(row, 0, legend_item)
            self.table.setItem(row, 1, material_item)
            self.table.setItem(row, 2, file_name_item)
            self.table.setItem(row, 3, file_path_item)

            file_name_item.setFlags(file_name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            file_path_item.setFlags(file_path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            material_item.setFlags(material_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_updated_legends(self):
        return [self.table.item(row, 0).text() for row in range(self.table.rowCount())]

    def get_selected_rows(self):
        return sorted(set(idx.row() for idx in self.table.selectedIndexes()), reverse=True)

    def delete_selected(self):
        rows = self.get_selected_rows()
        if not rows:
            return

        for row in rows:
            self.table.removeRow(row)
            del self.graph_info_list[row]

        if hasattr(self.parent(), 'figure'):
            ax = self.parent().figure.axes[0]
            lines = ax.get_lines()
            for idx in sorted(rows, reverse=True):
                if idx < len(lines):
                    lines[idx].remove()

            updated_legends = [self.table.item(row, 0).text() for row in range(self.table.rowCount())]
            for line, label in zip(ax.get_lines(), updated_legends):
                line.set_label(label)

            ax.legend()
            self.parent().canvas_plot.draw()


class InterfaceSettingsDialog(QDialog):
    def __init__(self, layers, interface_modes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interface Settings")
        self.resize(500, 300)

        self.layers = layers
        self.interface_modes = interface_modes

        layout = QVBoxLayout()
        self.table = QTableWidget(len(interface_modes), 4)
        self.table.setHorizontalHeaderLabels(["Interface", "Layer A", "Layer B", "Mode"])

        for i in range(len(interface_modes)):
            layer_a = layers[i]["type"]
            layer_b = layers[i+1]["type"]

            def count_same(layers, name, up_to):
                return sum(1 for l in layers[:up_to+1] if l["type"] == name)

            name_a = f"{layer_a} {count_same(layers, layer_a, i)}"
            name_b = f"{layer_b} {count_same(layers, layer_b, i+1)}"

            self.table.setItem(i, 0, QTableWidgetItem(f"Interface {i+1}"))
            self.table.setItem(i, 1, QTableWidgetItem(name_a))
            self.table.setItem(i, 2, QTableWidgetItem(name_b))

            mode_dropdown = QComboBox()
            mode_dropdown.addItems(["bonded", "unbonded"])
            mode_dropdown.setCurrentText(interface_modes[i])
            self.table.setCellWidget(i, 3, mode_dropdown)

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_interface_modes(self):
        modes = []
        for i in range(self.table.rowCount()):
            widget = self.table.cellWidget(i, 3)
            modes.append(widget.currentText())
        return modes


class SoundInsulationUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sound Insulation Performance")
        self.resize(1200, 800)

        self.layers = []
        self.active_layer_index = None
        self.interface_modes = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout()
        central_widget.setLayout(self.main_layout)

        self.init_left_panel()
        self.init_right_panel()

    # ----------
    # left panel
    # ----------
    def init_left_panel(self):
        left_panel = QWidget()
        left_panel.setFixedWidth(420)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        self.main_layout.addWidget(left_panel)

        self.layer_panel = QGroupBox("Layer Configuration")
        self.layer_panel.setFixedHeight(280)
        layer_panel_layout = QVBoxLayout()
        self.layer_panel.setLayout(layer_panel_layout)
        left_layout.addWidget(self.layer_panel)

        self.init_layer_configuration(layer_panel_layout)
        self.init_environment_panel(left_layout)

        self.property_panel = QGroupBox("Material Properties")
        scroll_area = QScrollArea()  # 스크롤 가능한 영역
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        self.property_layout = QVBoxLayout(scroll_content)
        scroll_content.setLayout(self.property_layout)

        scroll_area.setWidget(scroll_content)

        property_layout = QVBoxLayout(self.property_panel)
        property_layout.addWidget(scroll_area)
        left_layout.addWidget(self.property_panel)

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.setFixedHeight(40)

        self.calculate_button.clicked.connect(self.calculate_and_plot)
        left_layout.addWidget(self.calculate_button)

    def init_layer_configuration(self, parent_layout):
        layer_config_layout = QHBoxLayout()

        self.layer_type_dropdown = QComboBox()
        self.layer_type_dropdown.addItems(["Select Material"] + [k for k in MATERIAL_DEFINITIONS.keys() if k != "Unbonded"])

        self.layer_thickness_input = QLineEdit()
        self.layer_thickness_input.setPlaceholderText("Enter thickness [mm]")

        self.add_layer_button = QPushButton("Add Layer")
        self.add_layer_button.clicked.connect(self.add_layer)

        layer_config_layout.addWidget(self.layer_type_dropdown)
        layer_config_layout.addWidget(self.layer_thickness_input)
        layer_config_layout.addWidget(self.add_layer_button)

        parent_layout.addLayout(layer_config_layout)

        layer_visual_layout = QHBoxLayout()
        layer_visual_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.canvas = LayerCanvas(self.layers, self.on_layer_selected, self.get_active_layer_index)
        layer_visual_layout.addWidget(self.canvas)
        parent_layout.addLayout(layer_visual_layout)

        self.init_control_buttons(parent_layout)

    def init_control_buttons(self, parent_layout):
        control_buttons_layout = QGridLayout()

        self.move_left_button = QPushButton("◀ Move Left")
        self.move_right_button = QPushButton("Move Right ▶")
        self.delete_layer_button = QPushButton("Delete Selected")
        self.clear_layers_button = QPushButton("Clear All")

        self.move_left_button.clicked.connect(self.move_layer_left)
        self.move_right_button.clicked.connect(self.move_layer_right)
        self.delete_layer_button.clicked.connect(self.delete_selected_layer)
        self.clear_layers_button.clicked.connect(self.clear_all_layers)

        control_buttons_layout.addWidget(self.move_left_button, 0, 0)
        control_buttons_layout.addWidget(self.move_right_button, 0, 1)
        control_buttons_layout.addWidget(self.delete_layer_button, 1, 0)
        control_buttons_layout.addWidget(self.clear_layers_button, 1, 1)

        parent_layout.addLayout(control_buttons_layout)

    def init_environment_panel(self, parent_layout):
        environment_panel = QGroupBox("Environmental Parameters")
        environment_panel.setFixedHeight(90)
        environment_layout = QGridLayout()

        self.p0_input = QLineEdit()
        self.temp_input = QLineEdit()
        self.rh_input = QLineEdit()
        self.theta_input = QLineEdit()

        self.p0_input.setPlaceholderText("P0 [Pa]")
        self.p0_input.setText("101325")
        self.temp_input.setPlaceholderText("Temp [C]")
        self.temp_input.setText("20")
        self.rh_input.setPlaceholderText("RH (0~1)")
        self.rh_input.setText("0.2")
        self.theta_input.setPlaceholderText("Incident Angle [deg]")
        self.theta_input.setText("0")

        environment_layout.addWidget(QLabel("P0   [Pa]:"), 0, 0)
        environment_layout.addWidget(self.p0_input, 0, 1)
        environment_layout.addWidget(QLabel("T    [°C]:"), 0, 2)
        environment_layout.addWidget(self.temp_input, 0, 3)
        environment_layout.addWidget(QLabel("RH    [%]:"), 0, 4)
        environment_layout.addWidget(self.rh_input, 0, 5)
        environment_layout.addWidget(QLabel("Theta [°]:"), 1, 0)
        environment_layout.addWidget(self.theta_input, 1, 1)

        environment_panel.setLayout(environment_layout)
        parent_layout.addWidget(environment_panel)

    # -----------
    # right panel
    # -----------
    def init_right_panel(self):
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        self.main_layout.addWidget(right_panel)

        self.result_panel = QGroupBox("Result Plot")
        self.result_layout = QVBoxLayout()
        self.result_panel.setLayout(self.result_layout)
        right_layout.addWidget(self.result_panel)

        self.init_plot_area()

    def init_plot_area(self):
        self.figure = Figure(figsize=(5, 5))
        self.canvas_plot = FigureCanvas(self.figure)
        self.canvas_plot.setMinimumSize(QSize(700, 700))

        self.graph_tab_widget = QTabWidget()
        self.result_layout.addWidget(self.graph_tab_widget)

        # Graph Type Tab
        graph_type_tab = QWidget()
        graph_type_layout = QHBoxLayout()
        self.graph_type_dropdown = QComboBox()
        self.graph_type_dropdown.addItems(["Transmission Loss", "Absorption Coefficient"])
        self.graph_type_dropdown.setFixedSize(200, 30)
        self.graph_type_dropdown.currentTextChanged.connect(self.update_graph_by_dropdown)
        graph_type_layout.addWidget(QLabel("Graph Type:"))
        graph_type_layout.addWidget(self.graph_type_dropdown)
        graph_type_tab.setLayout(graph_type_layout)
        self.graph_tab_widget.addTab(graph_type_tab, "Graph Type")

        # Interface Manage Tab
        interface_tab = QWidget()
        interface_layout = QVBoxLayout()
        self.interface_settings_button = QPushButton("Open Interface Settings")
        self.interface_settings_button.setFixedSize(200, 30)
        self.interface_settings_button.clicked.connect(self.open_interface_settings_dialog)
        interface_layout.addWidget(self.interface_settings_button)
        interface_tab.setLayout(interface_layout)
        self.graph_tab_widget.addTab(interface_tab, "Interface Manage")

        # Canvas and Buttons Below
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.addWidget(self.canvas_plot)

        icon_buttons = [
            ("Zoom In", "zoom_in_button", lambda: self.zoom_plot(0.8)),
            ("Zoom Out", "zoom_out_button", lambda: self.zoom_plot(1.2)),
            ("Set Axis", "set_axis_range_button", self.open_axis_range_dialog),
            ("Reset", "reset_axis_button", self.reset_axis_range)
        ]

        for i, (label, attr, func) in enumerate(icon_buttons):
            btn = QPushButton()
            btn.setIcon(QIcon(os.path.join("icons", label.replace(" ", "_").lower() + ".png")))
            btn.setToolTip(label)
            btn.setFixedSize(48, 48)
            btn.setStyleSheet("border: none;")
            btn.clicked.connect(func)
            btn.setParent(self.canvas_plot)
            btn.move(10 + i * 40, 10)
            setattr(self, attr, btn)

        button_layout = QGridLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_results)
        self.load_graph_button = QPushButton("Load Graph")
        self.load_graph_button.clicked.connect(self.load_graph_csv)
        self.load_material_button = QPushButton("Load Material")
        self.load_material_button.clicked.connect(self.load_material_json)
        self.manage_legend_button = QPushButton("Edit Graph")
        self.manage_legend_button.clicked.connect(self.manage_legends)

        button_layout.addWidget(self.manage_legend_button)
        button_layout.addWidget(self.save_button, 0, 1)
        button_layout.addWidget(self.load_material_button, 1, 0)
        button_layout.addWidget(self.load_graph_button, 1, 1)

        canvas_layout.addLayout(button_layout)
        self.result_layout.addWidget(canvas_container)

    def zoom_plot(self, scale):
        if not self.figure.axes:
            return
        ax = self.figure.axes[0]
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        x_half_range = (x_max - x_min) * scale / 2
        y_half_range = (y_max - y_min) * scale / 2
        ax.set_xlim([x_center - x_half_range, x_center + x_half_range])
        ax.set_ylim([y_center - y_half_range, y_center + y_half_range])
        self.canvas_plot.draw()

    def reset_axis_range(self):
        if not self.figure.axes:
            return
        ax = self.figure.axes[0]
        ax.relim()
        ax.autoscale()
        self.canvas_plot.draw()

    def open_axis_range_dialog(self):
        dialog = AxisRangeDialog(self)
        if dialog.exec():
            try:
                x_min = float(dialog.xmin_input.text())
                x_max = float(dialog.xmax_input.text())
                y_min = float(dialog.ymin_input.text())
                y_max = float(dialog.ymax_input.text())

                ax = self.figure.axes[0]
                ax.set_xlim([x_min, x_max])
                ax.set_ylim([y_min, y_max])
                self.canvas_plot.draw()
            except ValueError:
                print("Invalid input for axis range.")

    # --------------------------------
    # button's functions at left panel
    # --------------------------------
    def add_layer(self):
        material_name = self.layer_type_dropdown.currentText()
        thickness_text = self.layer_thickness_input.text()

        if material_name == "Select Material":
            QMessageBox.warning(self, "Input Error", "Please select a material.", QMessageBox.StandardButton.Ok)
            return

        try:
            thickness = float(thickness_text)
            if thickness <= 0:
                raise ValueError("Thickness must be positive")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid thickness greater than 0.",
                                QMessageBox.StandardButton.Ok)
            return

        material_data = MATERIAL_DEFINITIONS.get(material_name, {})

        new_layer = {
            "material": material_name,
            "type": material_name,
            "thickness": thickness,
            "fields": [],
            "metadata": [],
            "values": material_data.copy()
        }

        self.layers.append(new_layer)
        self.canvas.repaint()

    def move_layer_left(self):
        i = self.active_layer_index
        if i is not None and i > 0:
            self.layers[i - 1], self.layers[i] = self.layers[i], self.layers[i - 1]
            self.active_layer_index -= 1
            self.canvas.repaint()
            self.on_layer_selected(self.active_layer_index)

    def move_layer_right(self):
        i = self.active_layer_index
        if i is not None and i < len(self.layers) - 1:
            self.layers[i + 1], self.layers[i] = self.layers[i], self.layers[i + 1]
            self.active_layer_index += 1
            self.canvas.repaint()
            self.on_layer_selected(self.active_layer_index)

    def delete_selected_layer(self):
        if self.active_layer_index is not None and 0 <= self.active_layer_index < len(self.layers):
            self.layers.pop(self.active_layer_index)
            self.active_layer_index = None
            self.canvas.repaint()
            self.clear_property_panel()

    def clear_all_layers(self):
        self.layers.clear()
        self.active_layer_index = None
        self.canvas.repaint()
        self.clear_property_panel()

    def update_graph_by_dropdown(self):
        if not hasattr(self, 'last_result_data'):
            return

        f, TL, alpha = self.last_result_data
        y_data = TL if self.graph_type_dropdown.currentText() == "Transmission Loss" else alpha
        y_label = "Transmission Loss [dB]" if self.graph_type_dropdown.currentText() == "Transmission Loss" else "Absorption Coefficient"

        if not self.figure.axes:
            ax = self.figure.add_subplot(111)
        else:
            ax = self.figure.axes[0]

        # 기존 그래프들을 유지하면서 새 plot만 갱신
        ax.clear()
        for info in getattr(self, 'graph_info_list', []):
            f_data = info.get('f')
            y_data_full = info.get('TL') if self.graph_type_dropdown.currentText() == "Transmission Loss" else info.get('alpha')
            label = info.get('legend')
            if f_data is not None and y_data_full is not None:
                ax.plot(f_data, y_data_full, linewidth=2, label=label)

        ax.set_xscale('log')
        ax.grid(True, which='both', linestyle='--')
        ax.set_xlabel('Frequency [Hz]', fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.legend()
        self.canvas_plot.draw()

    def calculate_and_plot(self):
        layer_data = self.prepare_calculation_data()
        try:
            theta = float(self.theta_input.text())
            P0 = float(self.p0_input.text())
            T = float(self.temp_input.text())
            RH = float(self.rh_input.text())

            save_json = False
            cleaned_layers = self.clean_layers_for_json(self.layers)

            if self.layers_differ(cleaned_layers):
                save_json = True

                # ✅ 사용자에게 저장 경로 직접 선택 받기
                json_path, _ = QFileDialog.getSaveFileName(
                    self, "Save Material Info JSON", "result_material.json", "JSON Files (*.json)")
                if not json_path:
                    print("[INFO] JSON save canceled by user.")
                    return

                material_info = {
                    "layers": cleaned_layers,
                    "environment": {
                        "theta": theta,
                        "P0": P0,
                        "T": T,
                        "RH": RH
                    }
                }
                with open(json_path, "w") as f:
                    json.dump(material_info, f, indent=2)

                self.last_saved_layers = copy.deepcopy(cleaned_layers)
                self.last_loaded_material_json_path = json_path

            else:
                json_path = getattr(self, "last_loaded_material_json_path", "-")

            f, TL, alpha, _, _ = run_simulation_from_ui(layer_data, theta_deg=theta, P0=P0, T=T, RH=RH)
            if f is None or TL is None:
                print("[ERROR] Simulation failed. No graph will be plotted.")
                return

            if not hasattr(self, 'calculate_counter'):
                self.calculate_counter = 1
            else:
                self.calculate_counter += 1

            legend_name = f'Calculate{self.calculate_counter}'
            if not hasattr(self, 'graph_info_list'):
                self.graph_info_list = []

            self.graph_info_list.append({
                "legend": legend_name,
                "material_info": os.path.basename(json_path),
                "file_path": json_path,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "f": f,
                "TL": TL,
                "alpha": alpha
            })

            self.last_result_data = (f, TL, alpha)
            self.last_result_legend = legend_name
            self.update_graph_by_dropdown()

            if save_json:
                print(f"[INFO] Material data saved to {json_path}")
            else:
                print("[INFO] Layer structure unchanged. Skipped material JSON save.")

        except Exception as e:
            print(f"[ERROR] Failed during calculation or plotting: {e}")

    def clean_layers_for_json(self, layers):
        cleaned_layers = []
        for layer in layers:
            cleaned_layer = {
                "type": layer["type"],
                "thickness": layer["thickness"],
                "values": layer.get("values", {})
            }
            cleaned_layers.append(cleaned_layer)
        return cleaned_layers

    def layers_differ(self, current_cleaned_layers):
        if not hasattr(self, 'last_saved_layers'):
            return True

        if len(current_cleaned_layers) != len(self.last_saved_layers):
            return True

        for l1, l2 in zip(current_cleaned_layers, self.last_saved_layers):
            if l1["type"] != l2["type"] or abs(l1["thickness"] - l2["thickness"]) > 1e-6:
                return True
            for key in l1["values"]:
                if key not in l2["values"]:
                    return True
                if abs(float(l1["values"][key]) - float(l2["values"][key])) > 1e-6:
                    return True
        return False

    def clear_property_panel(self):
        if self.active_layer_index is not None:
            layer = self.layers[self.active_layer_index]
            values = {}
            for name, _, field in layer.get("metadata", []):
                text = field.text()
                if text:
                    if name == "material":
                        values[name] = text.strip()
                    elif name == "thickness":
                        thickness_val = float(text)
                        layer["thickness"] = thickness_val
                        values[name] = thickness_val
                    else:
                        values[name] = float(text)
            layer["values"] = values

        for i in reversed(range(self.property_layout.count())):
            widget = self.property_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.canvas.repaint()

    def prepare_calculation_data(self):
        if self.active_layer_index is not None:
            self.clear_property_panel()

        calculation_layers = []
        for i, layer in enumerate(self.layers):
            entry = {
                "type": layer["type"],
                "thickness": layer["thickness"] / 1000.0
            }

            for key, value in layer.get("values", {}).items():
                if key not in ["thickness", "material"]:
                    try:
                        entry[key] = float(value)
                    except (ValueError, TypeError):
                        print(f"[WARNING] Layer {i + 1}: Invalid value for {key}: {value}")
                        continue

            calculation_layers.append(entry)
        return calculation_layers

    def on_layer_selected(self, index):
        if self.active_layer_index == index:
            self.clear_property_panel()
            self.active_layer_index = None
            self.canvas.repaint()
            return
        self.clear_property_panel()
        self.active_layer_index = index
        layer = self.layers[index]
        material_type = layer["type"]
        existing_values = layer.get("values", {})
        layer["fields"] = []
        layer["metadata"] = []
        for prop in MATERIAL_DEFINITIONS[material_type]["properties"]:
            label = QLabel(prop["label"])
            field = QLineEdit()
            if prop["name"] == "thickness":
                field.setText(str(layer["thickness"]))
            else:
                if prop["name"] in existing_values:
                    field.setText(str(existing_values[prop["name"]]))
            self.property_layout.addWidget(label)
            self.property_layout.addWidget(field)
            layer["fields"].append((label, field))
            layer["metadata"].append((prop["name"], prop["label"], field))
        self.canvas.repaint()

    def get_active_layer_index(self):
        return self.active_layer_index

    # --------------------------------
    # button's functions at right plot
    # --------------------------------
    def save_results(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Results")
        if not folder:
            return

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        base_name = f"result_{timestamp}"
        image_path = os.path.join(folder, f"{base_name}.png")
        csv_path = os.path.join(folder, f"{base_name}.csv")

        # 1. 그래프 이미지 저장
        try:
            self.figure.savefig(image_path)
            print(f"[INFO] Plot image saved to {image_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save plot image: {e}")

        # 2. CSV 저장 (graph_info_list 기준으로 모든 그래프 저장)
        try:
            if not hasattr(self, 'graph_info_list') or not self.graph_info_list:
                print("[INFO] No graph to save.")
                return

            # 메타정보 키 매핑
            key_map = {
                "material info.": "material_info",
                "path": "file_path",
                "date": "date",
                "graph name": "legend"
            }

            graphs = self.graph_info_list
            max_len = max(len(g["f"]) for g in graphs)

            # 메타데이터 행 구성
            metadata_rows_fixed = {}
            for i, (display_key, dict_key) in enumerate(key_map.items()):
                row = []
                for g in graphs:
                    row.extend([g.get(dict_key, "-"), "", ""])  # 정보 1개 + 빈칸 2개
                metadata_rows_fixed[i] = [display_key] + row

            # 데이터 본문 구성
            data_rows_fixed = {}
            for i in range(max_len):
                row = []
                for g in graphs:
                    if i < len(g["f"]):
                        row.extend([g["f"][i], g["TL"][i], g["alpha"][i]])
                    else:
                        row.extend(["", "", ""])
                data_rows_fixed[i] = row

            # 컬럼명 구성
            header_fixed = []
            for g in graphs:
                header_fixed.extend(["Frequency [Hz]", "Transmission Loss [dB]", "Absorption Coefficient"])
            header_fixed = [""] + header_fixed

            # 데이터프레임 구성
            df_fixed = pd.DataFrame.from_dict(data_rows_fixed, orient='index')
            df_fixed.columns = header_fixed[1:]

            # 메타 행 삽입
            for idx, meta_row in metadata_rows_fixed.items():
                df_fixed.loc[-(4 - idx)] = meta_row[1:]
            df_fixed.sort_index(inplace=True)

            # 메타 키 열 삽입
            meta_column = ["" for _ in range(len(df_fixed))]
            for idx, key in zip(range(-4, 0), key_map.keys()):
                meta_column[idx] = key
            df_fixed.insert(0, "", meta_column)

            # CSV 저장
            df_fixed.to_csv(csv_path, index=False)
            print(f"[INFO] Plot data saved to {csv_path}")

        except Exception as e:
            print(f"[ERROR] Failed to save CSV data: {e}")

    def load_material_json(self):
        json_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if not json_path:
            print("[INFO] Load canceled (JSON).")
            return

        try:
            with open(json_path, "r") as fjson:
                loaded = json.load(fjson)
                loaded_layers = loaded.get("layers", [])
                env = loaded.get("environment", {})

            self.theta_input.setText(str(env.get("theta", 90)))
            self.p0_input.setText(str(env.get("P0", 101325)))
            self.temp_input.setText(str(env.get("T", 20)))
            self.rh_input.setText(str(env.get("RH", 0.2)))

            self.layers.clear()
            for entry in loaded_layers:
                thickness_mm = entry.get("thickness", 0)
                material_type = entry.get("type", "")
                values = entry.get("values", {})
                self.layers.append({
                    "type": material_type,
                    "thickness": thickness_mm,
                    "fields": [],
                    "metadata": [],
                    "values": values
                })

            self.active_layer_index = None
            self.canvas.repaint()
            self.clear_property_panel()

            # ★ 저장한 json 경로를 기억해둠
            self.last_loaded_material_json_path = json_path

            print(f"[INFO] Loaded {len(self.layers)} layers from {os.path.basename(json_path)}")

        except Exception as e:
            print(f"[ERROR] Failed to load material JSON: {e}")

    def load_graph_csv(self):
        csv_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if not csv_path:
            print("[INFO] Load canceled (CSV).")
            return

        try:
            data = np.loadtxt(csv_path, delimiter=",", skiprows=1)
            f = data[:, 0]
            TL = data[:, 1] if data.shape[1] > 1 else None
            alpha = data[:, 2] if data.shape[1] > 2 else None

            if not hasattr(self, 'graph_counter'):
                self.graph_counter = 1
            else:
                self.graph_counter += 1

            legend_name = f'Data{self.graph_counter}'
            self.last_result_data = (f, TL, alpha)
            self.last_result_legend = legend_name

            # 기존처럼 저장
            if not hasattr(self, 'graph_info_list'):
                self.graph_info_list = []

            self.graph_info_list.append({
                "legend": legend_name,
                "file_name": os.path.basename(csv_path),
                "file_path": csv_path,
                "f": f,
                "TL": TL,
                "alpha": alpha
            })

            self.update_graph_by_dropdown()  # 전체 그래프 다시 그림
            print(f"[INFO] Plot loaded from {os.path.basename(csv_path)}")

        except Exception as e:
            print(f"[ERROR] Failed to load graph CSV: {e}")

    def manage_legends(self):
        if not hasattr(self, 'graph_info_list') or not self.graph_info_list:
            print("[INFO] No legends to manage.")
            return

        dialog = ManageLegendDialog(self.graph_info_list, self)
        if dialog.exec():
            updated_legends = dialog.get_updated_legends()

            if not self.figure.axes:
                print("[INFO] No active plot.")
                return

            ax = self.figure.axes[0]
            lines = ax.get_lines()

            # OK 버튼 누를 때는 이름만 변경
            for line, new_label in zip(lines, updated_legends):
                line.set_label(new_label)

            ax.legend()
            self.canvas_plot.draw()

    # ----------------
    # interface manage
    # ----------------
    def create_unbonded_layer(self):
        return {
            "type": "Unbonded",
            "thickness": 0.0001,
            "fields": [],
            "metadata": [],
            "values": {}
        }

    def count_interface_pairs(self):
        return sum(1 for i in range(len(self.layers) - 1)
                   if self.layers[i]["type"] != "Unbonded" and self.layers[i + 1]["type"] != "Unbonded")

    def open_interface_settings_dialog(self):
        if len(self.layers) < 2:
            QMessageBox.warning(self, "Warning", "At least two layers are required.")
            return

        if not self.interface_modes or len(self.interface_modes) != self.count_interface_pairs():
            self.interface_modes = ["bonded"] * self.count_interface_pairs()

        dialog = InterfaceSettingsDialog(self.layers, self.interface_modes, self)
        if dialog.exec():
            self.interface_modes = dialog.get_interface_modes()
            self.apply_interface_settings()

    def open_interface_settings_dialog(self):
        if len(self.layers) < 2:
            QMessageBox.warning(self, "Warning", "At least two layers are required.")
            return

        visible_layers = [layer for layer in self.layers if layer["type"] != "Unbonded"]

        # 인터페이스 수와 모드 배열 수가 다를 경우 보정
        if len(self.interface_modes) != len(visible_layers) - 1:
            self.interface_modes = ["bonded"] * (len(visible_layers) - 1)

        dialog = InterfaceSettingsDialog(visible_layers, self.interface_modes.copy(), self)
        if dialog.exec():
            updated_modes = dialog.get_interface_modes()
            self.apply_interface_settings(updated_modes)

    def apply_interface_settings(self, new_interface_modes):
        new_layers = []
        i = 0
        j = 0

        while i < len(self.layers):
            layer = self.layers[i]
            if layer["type"] == "Unbonded":
                i += 1
                continue

            new_layers.append(layer)

            if j < len(new_interface_modes):
                mode = new_interface_modes[j]
                if (i + 1 < len(self.layers)) and self.layers[i + 1]["type"] != "Unbonded":
                    if mode == "unbonded":
                        new_layers.append(self.create_unbonded_layer())
                j += 1

            i += 1

        self.layers = new_layers

        # 실제 반영된 구조 기준으로 재계산
        visible_layers = [l for l in self.layers if l["type"] != "Unbonded"]
        self.interface_modes = [
            "unbonded" if self.layers[i + 1]["type"] == "Unbonded" else "bonded"
            for i in range(len(visible_layers) - 1)
        ]

        self.canvas.repaint()