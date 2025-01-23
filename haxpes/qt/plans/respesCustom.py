from nbs_gui.plans.base import BasicPlanWidget
from nbs_gui.plans.planParam import AutoParamGroup
from nbs_gui.plans.sampleModifier import SampleSelectWidget
from nbs_gui.plans.scanModifier import ScanModifierParam, BeamlineModifierParam
from nbs_gui.plans.variableStepPlan import VariableStepParam
from .xpsParams import XPSParam, AnalyzerParam
from qtpy.QtWidgets import QGridLayout, QWidget, QHBoxLayout, QVBoxLayout
from bluesky_queueserver_api import BPlan


class RESPESCustomWidget(BasicPlanWidget):
    display_name = "RESPES Custom Scan"

    def __init__(
        self,
        model,
        parent=None,
        plans="RESPES_scan",
        **kwargs,
    ):
        self.initial_kwargs = kwargs

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
