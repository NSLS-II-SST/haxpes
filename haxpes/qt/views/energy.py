from qtpy.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QDialog,
    QComboBox,
)
from nbs_gui.views.views import AutoControl, AutoMonitor
from bluesky_queueserver_api import BPlan


class CrystalSelectionDialog(QDialog):
    """Dialog for selecting crystal settings.

    Parameters
    ----------
    parent : QWidget
        Parent widget
    crystal_model : object
        Model containing crystal settings
    """

    def __init__(self, parent, crystal_model):
        super().__init__(parent)
        self.setWindowTitle("Select Crystal")
        self.crystal_model = crystal_model

        layout = QVBoxLayout()

        self.cb = QComboBox()
        if hasattr(crystal_model, "enum_strs"):
            for s in crystal_model.enum_strs:
                if s != "":
                    self.cb.addItem(s)

        layout.addWidget(self.cb)

        button_box = QHBoxLayout()
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_box.addWidget(self.confirm_button)
        button_box.addWidget(self.cancel_button)
        layout.addLayout(button_box)

        self.setLayout(layout)

    def get_selected_crystal(self):
        """Get the selected crystal setting string."""
        return self.cb.currentText()


class SST2EnergyMonitor(QGroupBox):
    """Widget for controlling energy-related components.

    Parameters
    ----------
    energy : object
        Energy model containing energy, gap, and phase attributes
    parent_model : object
        Parent model containing beamline configuration
    orientation : str, optional
        Layout orientation
    *args, **kwargs
        Additional arguments passed to QGroupBox
    """

    def __init__(self, energy, parent_model, *args, orientation=None, **kwargs):
        print("Initializing Tender EnergyMonitor")
        super().__init__("Energy Monitor", *args, **kwargs)

        self.model = energy
        self.parent_model = parent_model
        self.REClientModel = parent_model.run_engine

        print("Creating Energy monitor layout")
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        ebox = QHBoxLayout()

        print("Adding energy monitor")
        if hasattr(energy, "energy"):
            ebox.addWidget(AutoMonitor(energy.energy, parent_model))

        vbox.addLayout(ebox)
        vbox.addWidget(AutoMonitor(energy.crystal, parent_model))

        hbox = QHBoxLayout()

        vbox.addLayout(hbox)
        self.setLayout(vbox)
        print("EnergyControl initialization complete")


class SST2EnergyControl(QGroupBox):
    """Widget for controlling energy-related components.

    Parameters
    ----------
    energy : object
        Energy model containing energy, gap, and phase attributes
    parent_model : object
        Parent model containing beamline configuration
    orientation : str, optional
        Layout orientation
    *args, **kwargs
        Additional arguments passed to QGroupBox
    """

    def __init__(self, energy, parent_model, *args, orientation=None, **kwargs):
        print("Initializing Tender EnergyControl")
        super().__init__("Energy Control", *args, **kwargs)

        self.model = energy
        self.parent_model = parent_model
        self.REClientModel = parent_model.run_engine

        print("Creating Tender Energy Control layout")
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        ebox = QHBoxLayout()

        print("Adding tender energy control")
        if hasattr(energy, "energy"):
            ebox.addWidget(AutoControl(energy.energy, parent_model))

        vbox.addLayout(ebox)
        vbox.addWidget(AutoMonitor(energy.crystal, parent_model))
        hbox = QHBoxLayout()

        print("Adding tune button")
        self.tuneButton = QPushButton("Tune X2 Pitch")
        self.tuneButton.clicked.connect(self.tune_x2pitch)
        hbox.addWidget(self.tuneButton)

        print("Adding crystal selection button")
        self.crystalButton = QPushButton("Set Crystal")
        self.crystalButton.clicked.connect(self.show_crystal_dialog)
        hbox.addWidget(self.crystalButton)

        vbox.addLayout(hbox)
        self.setLayout(vbox)
        print("EnergyControl initialization complete")

    def show_crystal_dialog(self):
        """Show crystal selection dialog."""
        print("Opening crystal selection dialog")
        if hasattr(self.model, "crystal"):
            dialog = CrystalSelectionDialog(self, self.model.crystal)
            if dialog.exec_() == QDialog.Accepted:
                crystal_setting = dialog.get_selected_crystal()
                print(f"Selected crystal setting: {crystal_setting}")
                msg = f"Are you sure you want to change to {crystal_setting}?"
                if self.confirm_dialog(msg):
                    plan = BPlan("set_crystal", crystal_setting)
                    self.REClientModel._client.item_execute(plan)

    def tune_x2pitch(self):
        """Execute x2pitch tuning plan."""
        print("Initiating x2pitch tune")
        msg = "Are you sure you want to tune the X2 pitch?"
        if self.confirm_dialog(msg):
            plan = BPlan("tune_x2pitch")
            self.REClientModel._client.item_execute(plan)

    def confirm_dialog(self, confirm_message):
        """Show a confirmation dialog.

        Parameters
        ----------
        confirm_message : str
            Message to display in the dialog

        Returns
        -------
        bool
            True if user confirmed, False otherwise
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(confirm_message)
        msg.setStyleSheet("button-layout: 1")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        ret = msg.exec_()
        return ret == QMessageBox.Yes
