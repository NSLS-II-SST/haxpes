from nbs_gui.plans.base import BasicPlanWidget
from nbs_gui.plans.planParam import AutoParamGroup
from nbs_gui.plans.sampleModifier import SampleSelectWidget
from nbs_gui.plans.scanModifier import ScanModifierParam, BeamlineModifierParam
from nbs_gui.plans.variableStepPlan import VariableStepParam
from .xpsParams import XPSParam, AnalyzerParam
from qtpy.QtWidgets import QGridLayout, QWidget, QHBoxLayout, QVBoxLayout
from bluesky_queueserver_api import BPlan


class XPSPlanWidget(BasicPlanWidget):
    def __init__(
        self,
        model,
        parent=None,
        plans="XPS_scan",
        **kwargs,
    ):
        self.initial_kwargs = kwargs
        self.display_name = "XPS"

        print("Initializing XPSPlanWidget Super")
        super().__init__(model, parent, plans)
        print("Done initializing XPSPlanWidget Super")

    def setup_widget(self):
        print("XPSPlanWidget setup Widget")
        super().setup_widget()
        self.scan_widget = XPSParam(self)
        self.params.append(self.scan_widget)
        self.scan_widget.editingFinished.connect(self.check_plan_ready)

        self.analyzer_widget = AnalyzerParam(self)
        self.params.append(self.analyzer_widget)

        self.scan_modifier = ScanModifierParam(self)
        self.params.append(self.scan_modifier)
        self.bl_modifier = BeamlineModifierParam(self.model, self)
        self.params.append(self.bl_modifier)

        self.sample_select = SampleSelectWidget(self.model, self)
        self.sample_select.editingFinished.connect(self.check_plan_ready)
        self.params.append(self.sample_select)

        # Create placeholder widgets for the 2x2 grid
        self.top_widget_layout = QHBoxLayout()
        self.bottom_widget_layout = QHBoxLayout()

        self.top_widget_layout.addWidget(self.scan_widget)
        self.top_widget_layout.addWidget(self.analyzer_widget)
        self.bottom_widget_layout.addWidget(self.sample_select)
        self.bottom_widget_layout.addWidget(self.scan_modifier)
        self.bottom_widget_layout.addWidget(self.bl_modifier)

        self.layout.addLayout(self.top_widget_layout)
        self.layout.addLayout(self.bottom_widget_layout)

        print("XPSPlanWidget setup Widget finished")

    def check_plan_ready(self):
        params = self.get_params()
        # modifier_params = self.scan_modifier.get_params()

        if (
            "num" in params
            and self.scan_modifier.check_ready()
            and self.sample_select.check_ready()
        ):
            self.plan_ready.emit(True)
        else:
            self.plan_ready.emit(False)

    def create_plan_items(self):
        params = self.get_params()
        samples = params.pop("samples", [{}])
        items = []

        for sample in samples:
            item = BPlan(
                "NewXPSScan",
                md={"scantype": "xps"},
                **params,
                **sample,
            )
            items.append(item)
        return items


class RESPESPlanWidget(BasicPlanWidget):
    def __init__(
        self,
        model,
        parent=None,
        plans="RESPES_scan",
        **kwargs,
    ):
        self.initial_kwargs = kwargs
        self.display_name = "RESPES"

        print("Initializing RESPESPlanWidget Super")
        super().__init__(model, parent, plans)
        print("Done initializing RESPESPlanWidget Super")

    def setup_widget(self):
        print("RESPESPlanWidget setup Widget")
        super().setup_widget()
        self.energy_widget = VariableStepParam(self)
        self.energy_widget.label_text = "Energy Step Arguments"
        self.params.append(self.energy_widget)

        self.scan_widget = XPSParam(self)
        self.params.append(self.scan_widget)
        self.scan_widget.editingFinished.connect(self.check_plan_ready)

        self.analyzer_widget = AnalyzerParam(self)
        self.params.append(self.analyzer_widget)

        self.scan_modifier = ScanModifierParam(self)
        self.params.append(self.scan_modifier)
        self.bl_modifier = BeamlineModifierParam(self.model, self)
        self.params.append(self.bl_modifier)

        self.sample_select = SampleSelectWidget(self.model, self)
        self.sample_select.editingFinished.connect(self.check_plan_ready)
        self.params.append(self.sample_select)

        # Create placeholder widgets for the 2x2 grid
        self.top_widget_layout = QHBoxLayout()
        self.bottom_widget_layout = QHBoxLayout()

        self.top_widget_layout.addWidget(self.scan_widget)
        self.top_widget_layout.addWidget(self.analyzer_widget)
        self.bottom_widget_layout.addWidget(self.sample_select)
        self.bottom_widget_layout.addWidget(self.scan_modifier)
        self.bottom_widget_layout.addWidget(self.bl_modifier)

        self.layout.addWidget(self.energy_widget)
        self.layout.addLayout(self.top_widget_layout)
        self.layout.addLayout(self.bottom_widget_layout)

        print("RESPESPlanWidget setup Widget finished")
