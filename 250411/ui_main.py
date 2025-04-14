from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox, QSizePolicy, QFileDialog
)
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

class SoundInsulationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Insulation Performance")
        self.resize(1300, 1000)

        self.layers = []
        self.active_layer_index = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel)

        self.layer_panel = QGroupBox("Layer Configuration & Visualization")
        self.layer_panel.setFixedHeight(350)
        layer_panel_layout = QVBoxLayout()
        self.layer_panel.setLayout(layer_panel_layout)
        left_layout.addWidget(self.layer_panel)

        # --- 위: 재료 선택 영역 ---
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
        layer_panel_layout.addLayout(layer_config_layout)

        # --- 캔버스 중심 수평 정렬 ---
        layer_visual_layout = QHBoxLayout()
        layer_visual_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.canvas = LayerCanvas(self.layers, self.on_layer_selected, self.get_active_layer_index)
        layer_visual_layout.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignVCenter)
        layer_panel_layout.addLayout(layer_visual_layout)

        # --- 버튼 3x2 배치 ---
        control_buttons_layout = QGridLayout()

        self.move_left_button = QPushButton("◀ Move Left")
        self.move_right_button = QPushButton("Move Right ▶")
        self.delete_layer_button = QPushButton("Delete Selected")
        self.clear_layers_button = QPushButton("Clear All")
        self.calculate_button = QPushButton("Calculate")

        self.move_left_button.clicked.connect(self.move_layer_left)
        self.move_right_button.clicked.connect(self.move_layer_right)
        self.delete_layer_button.clicked.connect(self.delete_selected_layer)
        self.clear_layers_button.clicked.connect(self.clear_all_layers)
        self.calculate_button.clicked.connect(self.calculate_and_plot)

        control_buttons_layout.addWidget(self.move_left_button, 0, 0)
        control_buttons_layout.addWidget(self.move_right_button, 0, 1)
        control_buttons_layout.addWidget(self.delete_layer_button, 1, 0)
        control_buttons_layout.addWidget(self.clear_layers_button, 1, 1)
        self.calculate_button.setMinimumHeight(30)
        control_buttons_layout.addWidget(self.calculate_button, 2, 0, 1, 2)

        layer_panel_layout.addLayout(control_buttons_layout)

        self.property_panel = QGroupBox("Material Properties")
        self.property_layout = QVBoxLayout()
        self.property_panel.setLayout(self.property_layout)
        left_layout.addWidget(self.property_panel)

        self.result_panel = QGroupBox("Result Plot")
        self.result_layout = QVBoxLayout()
        self.result_panel.setLayout(self.result_layout)
        right_layout.addWidget(self.result_panel)

        self.figure = Figure(figsize=(5, 5))  # 정사각형 비율 유지
        self.canvas_plot = FigureCanvas(self.figure)
        self.canvas_plot.setMinimumSize(QSize(400, 400))
        self.result_layout.addWidget(self.canvas_plot)

        axis_input_layout = QGridLayout()

        self.xmin_input = QLineEdit()
        self.xmax_input = QLineEdit()
        self.ymin_input = QLineEdit()
        self.ymax_input = QLineEdit()

        self.xmin_input.setPlaceholderText("x: from")
        self.xmax_input.setPlaceholderText("x: to")
        self.ymin_input.setPlaceholderText("y: from")
        self.ymax_input.setPlaceholderText("y: to")

        axis_input_layout.addWidget(QLabel("x:"), 0, 0)
        axis_input_layout.addWidget(self.xmin_input, 0, 1)
        axis_input_layout.addWidget(QLabel("to"), 0, 2)
        axis_input_layout.addWidget(self.xmax_input, 0, 3)

        axis_input_layout.addWidget(QLabel("y:"), 1, 0)
        axis_input_layout.addWidget(self.ymin_input, 1, 1)
        axis_input_layout.addWidget(QLabel("to"), 1, 2)
        axis_input_layout.addWidget(self.ymax_input, 1, 3)

        self.result_layout.addLayout(axis_input_layout)

        save_load_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Results")
        self.save_button.clicked.connect(self.save_results)

        self.load_button = QPushButton("Load Results")
        self.load_button.clicked.connect(self.load_results)

        save_load_layout.addWidget(self.save_button)
        save_load_layout.addWidget(self.load_button)
        self.result_layout.addLayout(save_load_layout)

        self.theta_input = QLineEdit()
        self.theta_input.setPlaceholderText("Incident Angle [deg]")
        self.theta_input.setText("90")

        self.p0_input = QLineEdit()
        self.p0_input.setPlaceholderText("P0 [Pa]")
        self.p0_input.setText("101325")

        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText("Temp [C]")
        self.temp_input.setText("20")

        self.rh_input = QLineEdit()
        self.rh_input.setPlaceholderText("RH (0~1)")
        self.rh_input.setText("0.2")

        air_theta_group = QGroupBox("Environmental Parameters")
        air_theta_group.setFixedHeight(100)
        air_theta_layout = QGridLayout()
        air_theta_layout.addWidget(QLabel("P0:"), 0, 0)
        air_theta_layout.addWidget(self.p0_input, 0, 1)
        air_theta_layout.addWidget(QLabel("T:"), 0, 2)
        air_theta_layout.addWidget(self.temp_input, 0, 3)
        air_theta_layout.addWidget(QLabel("RH:"), 0, 4)
        air_theta_layout.addWidget(self.rh_input, 0, 5)
        air_theta_layout.addWidget(QLabel("Theta:"), 1, 0)
        air_theta_layout.addWidget(self.theta_input, 1, 1)
        air_theta_group.setLayout(air_theta_layout)

        self.result_layout.insertWidget(0, air_theta_group)

    def clear_property_panel(self):
        if self.active_layer_index is not None:
            layer = self.layers[self.active_layer_index]
            values = {}
            for name, _, field in layer.get("metadata", []):
                text = field.text()
                if text:
                    print(f"[DEBUG] 읽은 입력값: name={name}, text={text}", flush=True)
                    if name == "material":
                        values[name] = text.strip()
                    else:
                        try:
                            values[name] = float(text)
                        except ValueError:
                            print(f"[WARNING] '{name}' 항목에 잘못된 값 '{text}' 입력됨", flush=True)
            layer["values"] = values

        for i in reversed(range(self.property_layout.count())):
            widget = self.property_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

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

    def calculate_and_plot(self):
        print("[DEBUG] calculate_and_plot 시작", flush=True)
        self.clear_property_panel()
        layer_data = self.prepare_calculation_data()

        try:
            theta = float(self.theta_input.text())
            P0 = float(self.p0_input.text())
            T = float(self.temp_input.text())
            RH = float(self.rh_input.text())
        except ValueError:
            print("[ERROR] Invalid air or angle input")
            return

        try:
            f, TL, _ = run_simulation_from_ui(layer_data, theta_deg=theta, P0=P0, T=T, RH=RH)
        except Exception as e:
            print(f"[ERROR] Simulation failed: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(f, TL, linewidth=2)
        ax.set_xscale('log')
        ax.grid(True, which='both', linestyle='--')
        ax.set_xlabel('Frequency [Hz]', fontsize=12)
        ax.set_ylabel('Transmission Loss [dB]', fontsize=12)

        def parse_float(text, default):
            try:
                return float(text)
            except ValueError:
                return default

        x_min = parse_float(self.xmin_input.text(), 100)
        x_max = parse_float(self.xmax_input.text(), 6400)
        y_min = parse_float(self.ymin_input.text(), 0)
        y_max = parse_float(self.ymax_input.text(), 100)

        ax.set_xlim([x_min, x_max])
        ax.set_ylim([y_min, y_max])

        self.canvas_plot.draw()

    def add_layer(self):
        material_type = self.layer_type_dropdown.currentText()
        thickness = self.layer_thickness_input.text()
        if material_type == "Select Material" or not thickness:
            return
        try:
            thickness_val = float(thickness)
        except ValueError:
            return
        layer_info = {
            "type": material_type,
            "thickness": thickness_val,
            "widget": None,
            "fields": [],
            "metadata": [],
            "values": {}
        }
        self.layers.append(layer_info)
        self.canvas.repaint()

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
                field.setReadOnly(True)
            else:
                if prop["name"] in existing_values:
                    field.setText(str(existing_values[prop["name"]]))
            self.property_layout.addWidget(label)
            self.property_layout.addWidget(field)
            layer["fields"].append((label, field))
            layer["metadata"].append((prop["name"], prop["label"], field))
        self.canvas.repaint()

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

    def get_active_layer_index(self):
        return self.active_layer_index

    def save_results(self):
        if self.figure.axes == []:
            print("[WARNING] No graph to save.")
            return

        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Results")
        if not folder:
            print("[INFO] Save canceled.")
            return

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        base_name = f"result_{timestamp}"

        image_path = os.path.join(folder, f"{base_name}.png")
        csv_path = os.path.join(folder, f"{base_name}.csv")
        json_path = os.path.join(folder, f"{base_name}.json")

        # --- Save figure ---
        self.figure.savefig(image_path)
        print(f"[INFO] Plot image saved to {image_path}")

        # --- Save CSV ---
        try:
            ax = self.figure.axes[0]
            lines = ax.get_lines()
            if not lines:
                print("[WARNING] No data lines in plot.")
                return
            y_data = lines[0].get_ydata()
            x_data = lines[0].get_xdata()
            np.savetxt(csv_path, np.column_stack((x_data, y_data)), delimiter=",",
                       header="Frequency [Hz],Transmission Loss [dB]", comments="")
            print(f"[INFO] CSV data saved to {csv_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save CSV: {e}")

        # --- Save layer info to JSON ---
        try:
            theta = float(self.theta_input.text())
            P0 = float(self.p0_input.text())
            T = float(self.temp_input.text())
            RH = float(self.rh_input.text())
        except ValueError:
            print("[ERROR] Invalid air or angle input during save.")
            theta, P0, T, RH = 90.0, 101325.0, 20.0, 0.2  # fallback to defaults

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
        print(f"[INFO] Layer & environment data saved to {json_path}")

    def load_results(self):
        # --- JSON (레이어 정보) 불러오기 ---
        json_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if not json_path:
            print("[INFO] Load canceled.")
            return

        with open(json_path, "r") as fjson:
            loaded = json.load(fjson)
            loaded_layers = loaded.get("layers", [])
            env = loaded.get("environment", {})
            self.theta_input.setText(str(env.get("theta", 90)))
            self.p0_input.setText(str(env.get("P0", 101325)))
            self.temp_input.setText(str(env.get("T", 20)))
            self.rh_input.setText(str(env.get("RH", 0.2)))

        # 레이어 정보 업데이트
        self.layers.clear()
        for entry in loaded_layers:
            thickness_mm = entry.get("thickness", 0) * 1000.0
            material_type = entry.get("type", "")
            values = {k: v for k, v in entry.items() if k not in ["thickness", "type"]}
            self.layers.append({
                "type": material_type,
                "thickness": thickness_mm,
                "widget": None,
                "fields": [],
                "metadata": [],
                "values": values
            })

        self.active_layer_index = None
        self.canvas.repaint()
        self.clear_property_panel()
        print(f"[INFO] Loaded {len(self.layers)} layers from {os.path.basename(json_path)}")

        # --- CSV (그래프 데이터) 불러오기 ---
        csv_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if not csv_path:
            print("[INFO] CSV load skipped.")
            return

        try:
            data = np.loadtxt(csv_path, delimiter=",", skiprows=1)
            f, TL = data[:, 0], data[:, 1]

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(f, TL, linewidth=2)
            ax.set_xscale('log')
            ax.grid(True, which='both', linestyle='--')
            ax.set_xlabel('Frequency [Hz]', fontsize=12)
            ax.set_ylabel('Transmission Loss [dB]', fontsize=12)
            ax.set_xlim([100, 6400])
            ax.set_ylim([0, 100])
            self.canvas_plot.draw()
            print(f"[INFO] Plot loaded from {os.path.basename(csv_path)}")
        except Exception as e:
            print(f"[ERROR] Failed to load CSV: {e}")