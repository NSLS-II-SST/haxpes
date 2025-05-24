from qtpy.QtWidgets import (
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
    QHBoxLayout,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)
from qtpy.QtCore import Signal, Qt
from bluesky_queueserver_api import BPlan, BFunc
from nbs_gui.plans.planParam import DynamicComboParam
from nbs_gui.plans.nbsPlan import NBSPlanWidget
from .xpsParams import AnalyzerParam
from nbs_gui.plans.sampleModifier import SampleSelectWidget
from nbs_gui.plans.scanModifier import ScanModifierParam, BeamlineModifierParam


class MultiXPSDialog(QDialog):
    def __init__(self, plans={}, parent=None):
        super().__init__(parent)

        self.list_widget = QListWidget()
        self.plan_keys = list(plans.keys())

        for k in self.plan_keys:
            item = QListWidgetItem(f"{plans[k].get('name', k)}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        # Add Check All and Uncheck All buttons
        self.check_all_button = QPushButton("Check All Plans")
        self.uncheck_all_button = QPushButton("Uncheck All Plans")
        self.check_all_button.clicked.connect(self.check_all_plans)
        self.uncheck_all_button.clicked.connect(self.uncheck_all_plans)

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.check_all_button)
        button_layout.addWidget(self.uncheck_all_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def check_all_plans(self):
        for index in range(self.list_widget.count()):
            self.list_widget.item(index).setCheckState(Qt.Checked)

    def uncheck_all_plans(self):
        for index in range(self.list_widget.count()):
            self.list_widget.item(index).setCheckState(Qt.Unchecked)

    def get_checked_plans(self):
        checked_plans = []
        for index in range(self.list_widget.count()):
            if self.list_widget.item(index).checkState() == Qt.Checked:
                checked_plans.append(self.plan_keys[index])
        return checked_plans


class XPSParam(DynamicComboParam):
    signal_update_region = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plans = {}
        self.input_widget.currentIndexChanged.connect(self.update_region)
        self.input_widget.currentIndexChanged.connect(self.clear_multiXPS)
        self.multiXPSButton = QPushButton("Multiple Plans")
        self.multiXPSButton.clicked.connect(self.show_multiXPSDialog)
        self.layout.addWidget(self.multiXPSButton)
        self.checked_plans = []

    def update_options(self, plans):
        current_text = self.input_widget.currentText()
        self.plans = plans
        self.input_widget.clear()
        self.input_widget.addItem(self.dummy_text)

        for key, plan_info in plans.items():
            name = plan_info.get("name", key)
            region = plan_info.get("region_dict", {})
            center = region.get("energy_center", None)
            width = region.get("energy_width", None)
            step = region.get("energy_step", None)
            energy_type = region.get("energy_type", None)
            if center is not None and width is not None:
                start = center - width / 2
                stop = center + width / 2
            else:
                start = None
                stop = None
            label = f"{name} ({start} to {stop} eV {energy_type}, {step} eV steps)"
            self.input_widget.addItem(str(label), userData=key)

        index = self.input_widget.findText(current_text)
        self.input_widget.setCurrentIndex(index if index >= 0 else 0)

    def clear_multiXPS(self):
        self.checked_plans = []
        self.input_widget.setItemText(0, self.dummy_text)

    def update_region(self):
        key = self.input_widget.currentData()
        plan_info = self.plans.get(key, {})
        core_line = str(plan_info.get("core_line", ""))
        self.signal_update_region.emit(core_line)

    def make_region_label(self):
        label = QLabel("")
        self.signal_update_region.connect(label.setText)
        return label

    def get_params(self):
        if self.input_widget.currentIndex() != 0:
            data = self.input_widget.currentData()
            print(f"Returning XPS {data}")
            return {"plan": data}
        elif self.checked_plans:
            return {"plan": self.checked_plans}
        return {}

    def show_multiXPSDialog(self):
        dialog = MultiXPSDialog(self.plans)
        if dialog.exec_() == QDialog.Accepted:
            self.input_widget.setCurrentIndex(0)
            self.checked_plans = dialog.get_checked_plans()
            if self.checked_plans:
                self.input_widget.setItemText(
                    0, f"{len(self.checked_plans)} selected plans"
                )
                self.editingFinished.emit()
            print(f"Checked plans: {self.checked_plans}")

    def check_ready(self):
        if self.input_widget.currentIndex() != 0 or self.checked_plans:
            return True
        return False


class XPSPlanWidget(NBSPlanWidget):
    signal_update_xps = Signal(object)
    display_name = "XPS Preset Region"

    def __init__(self, model, parent=None):
        print("Initializing XPS")

        super().__init__(
            model,
            parent,
            "dummy",
            layout_style=2,
        )
        self.signal_update_xps.connect(self.update_xps)
        self.user_status.register_signal("XPS_PLANS", self.signal_update_xps)
        print("XPS Initialized")

        # Add Load RSOXS button
        self.load_xps_button = QPushButton("Load XPS regions from file", self)
        self.load_xps_button.clicked.connect(self.load_xps_file)
        self.basePlanLayout.addWidget(self.load_xps_button)

    def reset(self):
        super().reset()
        self.user_status.register_signal("XPS_PLANS", self.signal_update_xps)

    def setup_widget(self):

        self.plans = {}
        self.region_selection = XPSParam(
            "region", "XPS Scan", "Select XPS Plan", parent=self
        )
        self.params.append(self.region_selection)
        self.region_selection.editingFinished.connect(self.check_plan_ready)

        print("XPSPlanWidget setup Widget")
        self.analyzer_widget = AnalyzerParam(self)
        self.params.append(self.analyzer_widget)
        self.analyzer_widget.editingFinished.connect(self.check_plan_ready)

        self.scan_modifier = ScanModifierParam(self)
        self.params.append(self.scan_modifier)
        self.scan_modifier.editingFinished.connect(self.check_plan_ready)

        self.bl_modifier = BeamlineModifierParam(self.model, self)
        self.params.append(self.bl_modifier)

        self.sample_select = SampleSelectWidget(self.model, self)
        self.sample_select.editingFinished.connect(self.check_plan_ready)
        self.params.append(self.sample_select)

        # Create placeholder widgets for the 2x2 grid
        self.top_widget_layout = QHBoxLayout()
        self.bottom_widget_layout = QHBoxLayout()
        self.layout.addWidget(self.region_selection)
        self.top_widget_layout.addWidget(self.analyzer_widget)
        self.top_widget_layout.addWidget(self.scan_modifier)
        self.bottom_widget_layout.addWidget(self.sample_select)
        self.bottom_widget_layout.addWidget(self.bl_modifier)

        self.layout.addLayout(self.top_widget_layout)
        self.layout.addLayout(self.bottom_widget_layout)

        print("XPSPlanWidget setup Widget finished")
        self.user_status.register_signal("XPS_PLANS", self.signal_update_xps)
        self.user_status.register_signal(
            "XPS_PLANS", self.region_selection.signal_update_options
        )

    def load_xps_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Excel Files (*.xls);;TOML files (*.toml)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                item = BFunc("load_xps", file_path)
                try:
                    # Load the XPS plans
                    self.run_engine_client._client.function_execute(item)

                    # Wait for function execution to complete
                    def condition(status):
                        return status["manager_state"] == "idle"

                    try:
                        self.run_engine_client._wait_for_completion(
                            condition=condition, msg="load XPS plans", timeout=10
                        )
                        # Now update the environment
                        self.run_engine_client.environment_update()
                    except Exception as wait_ex:
                        QMessageBox.warning(
                            self,
                            "XPS Load Warning",
                            f"XPS plans may not be fully loaded: {str(wait_ex)}",
                            QMessageBox.Ok,
                        )
                    return True
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "XPS Load Error",
                        f"Failed to load {file_path}: {str(e)}",
                        QMessageBox.Ok,
                    )
                    return False

    def check_plan_ready(self):
        """
        Check if all selections have been made and emit the plan_ready signal if they have.
        """
        if (
            self.region_selection.check_ready()
            and self.analyzer_widget.check_ready()
            and self.scan_modifier.check_ready()
            and self.sample_select.check_ready()
        ):
            self.plan_ready.emit(True)
        else:
            self.plan_ready.emit(False)

    def update_xps(self, plan_dict):
        self.xps_plans = plan_dict
        self.region_selection.signal_update_options.emit(self.xps_plans)
        self.widget_updated.emit()

    def create_plan_items(self):
        params = self.get_params()
        print(params)
        plan = params.pop("plan")
        samples = params.pop("samples", [{}])
        items = []

        if isinstance(plan, list):
            for s in samples:
                for p in plan:
                    item = BPlan(p, **s, **params)
                    items.append(item)
        else:
            for s in samples:
                item = BPlan(plan, **s, **params)
                items.append(item)
        return items
