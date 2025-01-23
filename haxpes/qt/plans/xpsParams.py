from nbs_gui.plans.planParam import (
    ParamGroup,
    LineEditParam,
    ComboBoxParam,
    SpinBoxParam,
)


class RegionParam(ParamGroup):
    def __init__(self, parent=None):
        super().__init__(parent, "XPS Parameters")

        self.add_param(LineEditParam("region_name", str, "Region Name"))
        self.add_param(
            ComboBoxParam("energy_type", ["binding", "kinetic"], "Energy Type")
        )
        self.add_param(LineEditParam("energy_center", float, "Energy Center"))
        self.add_param(
            LineEditParam(
                "energy_step",
                float,
                "Energy Step",
                "Energy step to set at plan start",
            )
        )
        self.add_param(
            LineEditParam("energy_width", float, "Energy Width", "Energy width to set")
        )

    def get_params(self):
        all_params = super().get_params()
        return {"region_dictionary": all_params}


class AnalyzerParam(ParamGroup):
    def __init__(self, parent=None):
        super().__init__(parent, "Analyzer Parameters")
        self.add_param(
            SpinBoxParam(
                "sweeps",
                "Sweeps",
                "Number of Analyzer Sweeps",
                value_type=int,
                default=1,
            )
        )
        self.add_param(
            SpinBoxParam(
                "dwell_time",
                "Dwell Time",
                "Analyzer Dwell Time",
                value_type=float,
                default=0.1,
            )
        )
        print("Adding pass energy param")
        self.add_param(
            ComboBoxParam("pass_energy", [20, 50, 100, 200, 500], "Pass Energy")
        )
        print("Adding lens mode param")
        self.add_param(
            ComboBoxParam("lens_mode", ["Angular", "Transmission"], "Lens Mode")
        )
        print("Done adding lens mode param")

    def get_params(self):
        all_params = super().get_params()
        sweeps = all_params.pop("sweeps")
        return {"analyzer_settings": all_params, "sweeps": sweeps}
