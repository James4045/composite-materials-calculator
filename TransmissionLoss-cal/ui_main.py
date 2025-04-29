from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox, QSizePolicy, QFileDialog, QDialog,
    QScrollArea, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt, QSize
import os
import sys
import numpy as np
import json
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

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

class ManageLegendDialog(QDialog):
    def __init__(self, graph_info_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Graph Info")
        self.resize(600, 400)
        self.graph_info_list = graph_info_list

        layout = QVBoxLayout()

        self.table = QTableWidget(len(graph_info_list), 3)
        self.table.setHorizontalHeaderLabels(["Legend Name", "File Name", "File Path"])

        for row, info in enumerate(graph_info_list):
            legend_item = QTableWidgetItem(info["legend"])
            file_name_item = QTableWidgetItem(info["file_name"])
            file_path_item = QTableWidgetItem(info["file_path"])

            self.table.setItem(row, 0, legend_item)
            self.table.setItem(row, 1, file_name_item)
            self.table.setItem(row, 2, file_path_item)

            file_name_item.setFlags(file_name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            file_path_item.setFlags(file_path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.delete_button = QPushButton("Delete Selected")

        self.ok_button.clicked.connect(self.accept)
        self.delete_button.clicked.connect(self.delete_selected)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_updated_legends(self):
        updated = []
        for row in range(self.table.rowCount()):
            updated.append(self.table.item(row, 0).text())
        return updated

    def get_selected_rows(self):
        return sorted(set(idx.row() for idx in self.table.selectedIndexes()), reverse=True)

    def delete_selected(self):
        rows = self.get_selected_rows()
        if not rows:
            return

        # 테이블, graph_info_list 삭제
        for row in rows:
            self.table.removeRow(row)
            del self.graph_info_list[row]

        # matplotlib 그래프에서도 삭제
        if hasattr(self.parent(), 'figure'):
            ax = self.parent().figure.axes[0]
            lines = ax.get_lines()
            for idx in sorted(rows, reverse=True):
                if idx < len(lines):
                    lines[idx].remove()

            self.parent().canvas_plot.draw()

class SoundInsulationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Insulation Performance")
        self.resize(1300, 1000)

        self.layers = []
        self.active_layer_index = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout()
        central_widget.setLayout(self.main_layout)

        self.init_left_panel()
        self.init_right_panel()

    def init_left_panel(self):
        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        self.main_layout.addWidget(left_panel)

        self.layer_panel = QGroupBox("Layer Configuration and Visualization")
        self.layer_panel.setFixedHeight(300)
        layer_panel_layout = QVBoxLayout()
        self.layer_panel.setLayout(layer_panel_layout)
        left_layout.addWidget(self.layer_panel)

        self.init_layer_configuration(layer_panel_layout)

        self.init_environment_panel(left_layout)

        self.property_panel = QGroupBox("Material Properties")
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        self.property_layout = QVBoxLayout(scroll_content)
        scroll_content.setLayout(self.property_layout)

        scroll_area.setWidget(scroll_content)

        property_layout = QVBoxLayout(self.property_panel)
        property_layout.addWidget(scroll_area)

        left_layout.addWidget(self.property_panel)

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate_and_plot)
        left_layout.addWidget(self.calculate_button)

    def init_layer_configuration(self, parent_layout):
        layer_config_layout = QHBoxLayout()
        self.layer_type_dropdown = QComboBox()
        self.layer_type_dropdown.addItems(["Select Material"] + list(MATERIAL_DEFINITIONS.keys()))
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
        environment_panel.setFixedHeight(100)
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
        self.init_axis_input_panel()
        self.init_save_load_buttons()

    def init_plot_area(self):
        self.figure = Figure(figsize=(5, 5))
        self.canvas_plot = FigureCanvas(self.figure)
        self.canvas_plot.setMinimumSize(QSize(400, 400))
        self.result_layout.addWidget(self.canvas_plot)

    def init_axis_input_panel(self):
        axis_button_layout = QHBoxLayout()
        self.set_axis_range_button = QPushButton("Set Axis Range")
        self.set_axis_range_button.clicked.connect(self.open_axis_range_dialog)
        axis_button_layout.addWidget(self.set_axis_range_button)
        self.result_layout.addLayout(axis_button_layout)

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

    def init_save_load_buttons(self):
        save_load_layout = QGridLayout()

        self.save_button = QPushButton("Save Results")
        self.save_button.clicked.connect(self.save_results)

        self.load_graph_button = QPushButton("Load Graph (.csv)")
        self.load_graph_button.clicked.connect(self.load_graph_csv)

        self.load_material_button = QPushButton("Load Material (.json)")
        self.load_material_button.clicked.connect(self.load_material_json)

        self.manage_legend_button = QPushButton("Edit Graph Info")
        self.manage_legend_button.clicked.connect(self.manage_legends)

        save_load_layout.addWidget(self.save_button, 1, 0)
        save_load_layout.addWidget(self.load_graph_button, 1, 1)
        save_load_layout.addWidget(self.load_material_button, 1, 2)
        save_load_layout.addWidget(self.manage_legend_button, 0, 0, 0, 3)

        self.result_layout.addLayout(save_load_layout)



    # ------------------------------------
    # buttons at layer configuration panel
    # linked buttons
    # ------------------------------------
    def add_layer(self):
        material_type = self.layer_type_dropdown.currentText()
        thickness = self.layer_thickness_input.text()
        thickness_val = float(thickness)
        layer_info = {
            "type": material_type,
            "thickness": thickness_val,
            "fields": [],
            "metadata": [],
            "values": {}
        }
        self.layers.append(layer_info)
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

    def calculate_and_plot(self):
        layer_data = self.prepare_calculation_data()

        try:
            theta = float(self.theta_input.text())
            P0 = float(self.p0_input.text())
            T = float(self.temp_input.text())
            RH = float(self.rh_input.text())

            f, TL, _ = run_simulation_from_ui(layer_data, theta_deg=theta, P0=P0, T=T, RH=RH)

            if f is None or TL is None:
                print("[ERROR] Simulation failed. No graph will be plotted.")
                return

            if not self.figure.axes:
                ax = self.figure.add_subplot(111)
            else:
                ax = self.figure.axes[0]

            if not hasattr(self, 'calculate_counter'):
                self.calculate_counter = 1
            else:
                self.calculate_counter += 1

            legend_name = f'Calculate{self.calculate_counter}'
            ax.plot(f, TL, linewidth=2, label=legend_name)
            ax.set_xscale('log')
            ax.grid(True, which='both', linestyle='--')
            ax.set_xlabel('Frequency [Hz]', fontsize=12)
            ax.set_ylabel('Transmission Loss [dB]', fontsize=12)
            ax.legend()

            if not hasattr(self, 'graph_info_list'):
                self.graph_info_list = []
            self.graph_info_list.append({
                "legend": legend_name,
                "file_name": "Generated Internally",
                "file_path": "-"
            })

            self.canvas_plot.draw()

        except Exception as e:
            print(f"[ERROR] Failed during calculation or plotting: {e}")

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

    # ----------------------
    # buttons at result plot
    # linked buttons
    # ----------------------
    def save_results(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Results")

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        base_name = f"result_{timestamp}"

        image_path = os.path.join(folder, f"{base_name}.png")
        csv_path = os.path.join(folder, f"{base_name}.csv")
        json_path = os.path.join(folder, f"{base_name}.json")

        # --- Save figure ---
        self.figure.savefig(image_path)

        # --- Save CSV ---
        ax = self.figure.axes[0]
        lines = ax.get_lines()
        y_data = lines[0].get_ydata()
        x_data = lines[0].get_xdata()
        np.savetxt(csv_path, np.column_stack((x_data, y_data)), delimiter=",",
                    header="Frequency [Hz],Transmission Loss [dB]", comments="")

        # --- Save JSON ---
        try:
            theta = float(self.theta_input.text())
            P0 = float(self.p0_input.text())
            T = float(self.temp_input.text())
            RH = float(self.rh_input.text())
        except ValueError:
            theta, P0, T, RH = 90.0, 101325.0, 20.0, 0.2

        layer_data = self.prepare_calculation_data()
        additional_info = {
            "theta": theta,
            "P0": P0,
            "T": T,
            "RH": RH
        }
        save_package = {
            "layers": layer_data,
            "environment": additional_info
        }
        with open(json_path, "w") as fjson:
            json.dump(save_package, fjson, indent=2)

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

            # 환경 변수 복원
            self.theta_input.setText(str(env.get("theta", 90)))
            self.p0_input.setText(str(env.get("P0", 101325)))
            self.temp_input.setText(str(env.get("T", 20)))
            self.rh_input.setText(str(env.get("RH", 0.2)))

            # 레이어 복원
            self.layers.clear()
            for entry in loaded_layers:
                thickness_mm = entry.get("thickness", 0) * 1000.0
                material_type = entry.get("type", "")
                values = {k: v for k, v in entry.items() if k not in ["thickness", "type"]}
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
            f, TL = data[:, 0], data[:, 1]

            if not self.figure.axes:
                ax = self.figure.add_subplot(111)
            else:
                ax = self.figure.axes[0]

            if not hasattr(self, 'graph_counter'):
                self.graph_counter = 1
            else:
                self.graph_counter += 1

            legend_name = f'Data{self.graph_counter}'
            ax.plot(f, TL, linewidth=2, label=legend_name)
            ax.set_xscale('log')
            ax.grid(True, which='both', linestyle='--')
            ax.set_xlabel('Frequency [Hz]', fontsize=12)
            ax.set_ylabel('Transmission Loss [dB]', fontsize=12)
            ax.legend()

            if not hasattr(self, 'graph_info_list'):
                self.graph_info_list = []
            self.graph_info_list.append({
                "legend": legend_name,
                "file_name": os.path.basename(csv_path),
                "file_path": csv_path
            })

            self.canvas_plot.draw()

            print(f"[INFO] Plot loaded from {os.path.basename(csv_path)}")

        except Exception as e:
            print(f"[ERROR] Failed to load graph CSV: {e}")

    def clear_graph(self):
        self.figure.clear()
        self.canvas_plot.draw()
        self.graph_counter = 0
        self.calculate_counter = 0
        self.graph_info_list = []

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