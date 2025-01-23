from qtpy.QtWidgets import QMessageBox
from qtpy.QtCore import Signal
from bluesky_queueserver_api import BPlan
from nbs_gui.plans.planLoaders import PlanLoaderWidgetBase


class XPSPlanLoader(PlanLoaderWidgetBase):
    display_name = "XPS Plans"
    signal_update_plans = Signal(object)
    signal_update_samples = Signal(object)

    def __init__(self, model, parent=None):
        super().__init__(model, parent)
        self.plans = {}
        self.signal_update_plans.connect(self.update_plans)
        self.user_status.register_signal("XPS_PLANS", self.signal_update_plans)

        self.signal_update_samples.connect(self.update_samples)
        self.user_status.register_signal("GLOBAL_SAMPLES", self.signal_update_samples)

    def update_plans(self, plans):
        self.plans = plans

    def update_samples(self, sample_dict):
        self.samples = sample_dict

    def get_plan(self, plan_name):
        plan_name = plan_name.lower()
        if plan_name in self.plans:
            return plan_name
        else:
            for plan_key, plan_info in self.plans.items():
                if plan_name in [
                    plan_info.get("name", "").lower(),
                    plan_info.get("core_line", "").lower(),
                ]:
                    return plan_key
        raise KeyError(f"{plan_name} not found in list of XPS Plans")

    def create_plan_items(self):
        items = []
        for plan_data in self.plan_queue_data:
            sample_id = plan_data.get("Sample ID")
            plan_name = plan_data.get("Plan")

            try:
                plan = self.get_plan(plan_name)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Plan Generation Error",
                    f"Failed to create plan: {str(e)}",
                    QMessageBox.Ok,
                )
                return []

            if sample_id not in self.samples:
                QMessageBox.critical(
                    self,
                    "Plan Generation Error",
                    f"Sample: {sample_id} not in sample list",
                    QMessageBox.Ok,
                )
                return []

            plan_kwargs = {}
            analyzer_dict = {}
            analyzer_dict["dwell_time"] = float(plan_data.get("Dwell Time", 0.01))
            analyzer_dict["lens_mode"] = plan_data.get("Lens Mode", "Angular")
            analyzer_dict["pass_energy"] = float(plan_data.get("Pass Energy", 50))
            plan_kwargs["group_name"] = plan_data.get("Group Name", None)
            plan_kwargs["comment"] = plan_data.get("Comment", None)
            plan_kwargs["repeat"] = int(plan_data.get("Repeat", 1))
            plan_kwargs["sweeps"] = int(plan_data.get("Sweeps", 1))
            plan_kwargs["analyzer_settings"] = analyzer_dict

            item = BPlan(plan, sample=sample_id, **plan_kwargs)
            items.append(item)
        return items
