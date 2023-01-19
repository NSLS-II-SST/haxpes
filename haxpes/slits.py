from ophyd import EpicsMotor, PseudoPositioner, PseudoSingle, Component as Cpt
from ophyd.pseudopos import pseudo_position_argument, real_position_argument
from sst_funcs.printing import boxed_text


class Slits(PseudoPositioner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # The pseudo positioner axes:
    vsize = Cpt(PseudoSingle, limits=None, kind="hinted")
    vcenter = Cpt(PseudoSingle, limits=None, kind="normal")
    hsize = Cpt(PseudoSingle, limits=None, kind="hinted")
    hcenter = Cpt(PseudoSingle, limits=None, kind="normal")

    # The real (or physical) positioners:
    top = Cpt(EpicsMotor, "T}Mtr", kind="normal")
    bottom = Cpt(EpicsMotor, "B}Mtr", kind="normal")
    inboard = Cpt(EpicsMotor, "I}Mtr", kind="normal")
    outboard = Cpt(EpicsMotor, "O}Mtr", kind="normal")

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        """Run a forward (pseudo -> real) calculation"""
        return self.RealPosition(
            top=pseudo_pos.vcenter + pseudo_pos.vsize / 2,
            bottom=pseudo_pos.vcenter - pseudo_pos.vsize / 2,
            outboard=pseudo_pos.hcenter + pseudo_pos.hsize / 2,
            inboard=pseudo_pos.hcenter - pseudo_pos.hsize / 2,
        )

    @real_position_argument
    def inverse(self, real_pos):
        """Run an inverse (real -> pseudo) calculation"""
        return self.PseudoPosition(
            hsize=real_pos.outboard - real_pos.inboard,
            hcenter=(real_pos.outboard + real_pos.inboard) / 2,
            vsize=real_pos.top - real_pos.bottom,
            vcenter=(real_pos.top + real_pos.bottom) / 2,
        )
