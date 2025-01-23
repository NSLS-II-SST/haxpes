from nbs_gui.plans.base import BasicPlanWidget
from nbs_gui.plans.planParam import AutoParamGroup
from nbs_gui.plans.sampleModifier import SampleSelectWidget
from nbs_gui.plans.scanModifier import ScanModifierParam, BeamlineModifierParam
from nbs_gui.plans.variableStepPlan import VariableStepParam
from .xpsParams import RegionParam, AnalyzerParam
from qtpy.QtWidgets import QGridLayout, QWidget, QHBoxLayout, QVBoxLayout
from bluesky_queueserver_api import BPlan


class XPSCustomWidget(BasicPlanWidget):
    display_name = "XPS Custom Region"

    def __init__(
        self,
        model,
        parent=None,
        plans="XPSScan",
        **kwargs,
    ):
        self.initial_kwargs = kwargs

        print("Initializing XPSCustomWidget Super")
        super().__init__(model, parent, plans)
        print("Done initializing XPSCustomWidget Super")

    def setup_widget(self):
        print("XPSCustomWidget setup Widget")
        super().setup_widget()
        self.scan_widget = RegionParam(self)
        self.params.append(self.scan_widget)
        self.scan_widget.editingFinished.connect(self.check_plan_ready)

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

        self.top_widget_layout.addWidget(self.scan_widget)
        self.top_widget_layout.addWidget(self.analyzer_widget)
        self.bottom_widget_layout.addWidget(self.sample_select)
        self.bottom_widget_layout.addWidget(self.scan_modifier)
        self.bottom_widget_layout.addWidget(self.bl_modifier)

        self.layout.addLayout(self.top_widget_layout)
        self.layout.addLayout(self.bottom_widget_layout)

        print("XPSCustomWidget setup Widget finished")

    def check_plan_ready(self):
        if (
            self.scan_widget.check_ready()
            and self.analyzer_widget.check_ready()
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
                "XPSScan",
                **params,
                **sample,
            )
            items.append(item)
        return items
