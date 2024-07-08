import sys
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QApplication, QVBoxLayout, QPushButton, QFileDialog, QListWidget, QAbstractItemView, QMessageBox, QMenu, QAction, QLabel, QLineEdit, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar
import matplotlib.pyplot as plt
from utils.data_handling import DataObject,DataDictionary    
from utils.data_transforms import *

class PeakPlottingProgramMain(QDialog):
    def __init__(self,parent=None):
        #make window form
        super(PeakPlottingProgramMain,self).__init__(parent)
        main_layout = QHBoxLayout()
        
        #plotting window section:
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavToolbar(self.canvas,self)
        self.buttonplotsel = QPushButton('Plot Selected')
        self.buttonplotsel.clicked.connect(lambda: self.replot())
        self.buttonplotcol = QPushButton('Plot Columns')
        self.buttonplotcol.clicked.connect(lambda: self.plot_multicolumn())
        self.xaxismenu = QMenu()
        KEaction = QAction("Kinetic Energy",self)
        KEaction.triggered.connect(lambda: self.plot_KE())
        BEaction = QAction("Binding Energy",self)
        BEaction.triggered.connect(lambda: self.plot_BE())
        self.xaxismenu.addAction(KEaction)
        self.xaxismenu.addAction(BEaction)
        self.xaxisbutton = QPushButton('X Axis Select')
        self.xaxisbutton.setMenu(self.xaxismenu)
        plot_layout = QVBoxLayout()
        plot_sublayout1 = QHBoxLayout()
        plot_sublayout1.addWidget(self.xaxisbutton)
        plot_sublayout1.addWidget(self.buttonplotsel)
        plot_sublayout1.addWidget(self.buttonplotcol)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)
        plot_layout.addLayout(plot_sublayout1)
        
        #data handling widget:
        self.opensesbutton = QPushButton('Load SES Data')
        self.opensesbutton.clicked.connect(lambda: self.load_data("ses"))
        self.openxybutton = QPushButton('Load XY Data')
        self.openxybutton.clicked.connect(lambda: self.load_data("peak"))
        self.clearbutton = QPushButton('Remove All')
        self.clearbutton.clicked.connect(lambda: self.clear_data())
        self.removeselbutton = QPushButton('Remove Selected')
        self.removeselbutton.clicked.connect(lambda: self.remove_selected())
        self.selectallbutton = QPushButton('Select All')
        self.selectallbutton.clicked.connect(lambda: self.select_all())
        self.exportbutton = QPushButton('Export Selected')
        self.exportbutton.clicked.connect(lambda: self.export_data())
        self.mdbutton = QPushButton('Show Meta')
        self.mdbutton.clicked.connect(lambda: self.show_metadata())
        self.datalist = QListWidget()
        self.datalist.setSelectionMode(QAbstractItemView.ExtendedSelection)
        data_layout = QVBoxLayout()
        data_layout.addWidget(self.opensesbutton)
        data_layout.addWidget(self.openxybutton)
        data_layout.addWidget(self.selectallbutton)
        data_layout.addWidget(self.exportbutton)
        data_layout.addWidget(self.mdbutton)
        data_layout.addWidget(self.datalist)
        data_layout.addWidget(self.removeselbutton)
        data_layout.addWidget(self.clearbutton)
        
        #data transforms section
        self.normleftbutton = QPushButton('Normalize Left')
        self.normleftbutton.clicked.connect(lambda: self.normalize_left())
        self.normrightbutton = QPushButton('Normalize Right')
        self.normrightbutton.clicked.connect(lambda: self.normalize_right())
        self.normmaxbutton = QPushButton('Normalize to Max.')
        self.normmaxbutton.clicked.connect(lambda: self.norm_max())
        self.normminmaxbutton = QPushButton('Normalize Min. to Max.')
        self.normminmaxbutton.clicked.connect(lambda: self.norm_min_max())
        self.subleftbutton = QPushButton('Subtract HLine Left')
        self.subleftbutton.clicked.connect(lambda: self.subline_left())
        self.subrightbutton = QPushButton('Subtract HLine Right')
        self.subrightbutton.clicked.connect(lambda: self.subline_right())
        self.revertbutton = QPushButton('Revert Selected')
        self.revertbutton.clicked.connect(lambda: self.revert())
        self.autoshiftbutton = QPushButton('Auto Shift Max.')
        self.autoshiftbutton.clicked.connect(lambda: self.autoshift())
        trans_layout = QVBoxLayout()
        trans_layout.addWidget(self.normleftbutton)
        trans_layout.addWidget(self.normrightbutton)
        trans_layout.addWidget(self.normmaxbutton)
        trans_layout.addWidget(self.normminmaxbutton)
        trans_layout.addWidget(self.subleftbutton)
        trans_layout.addWidget(self.subrightbutton)
        trans_layout.addWidget(self.autoshiftbutton)
        trans_layout.addWidget(self.revertbutton)

        #main layout ...
        main_layout.addLayout(trans_layout)
        main_layout.addLayout(plot_layout)
        main_layout.addLayout(data_layout)
        
        self.setLayout(main_layout)
        self.setGeometry(50,50,960,640)
        self.setWindowTitle("SST-2 HAXPES Plotting Program")

        #initialize items:
        self.ddict = DataDictionary()
        self.xaxis = "Kinetic"
        self.xlabel = "Kinetic Energy (eV)"
        self.ylabel = "Intensity (arb.)"
        self.selecteddatanames = []

    #functions
    def load_data(self,dataformat):
        # TO DO: data formats ...
        filelist = QFileDialog.getOpenFileNames(self,'Select Files')[0] #TO DO: filters
        for fpath in filelist:
            D = DataObject()
            D.load_from_ascii(fpath)
            self.ddict.append_data(D.name,D)
            self.datalist.addItem(D.name)

    def replot(self):
        self.get_selection()
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        if self.xaxis == "Binding":
            self.xlabel = "Binding Energy (eV)"
            ax.invert_xaxis()
        elif self.xaxis == "Kinetic":
            self.xlabel = "Kinetic Energy (eV)"
        for dataname in self.selecteddatanames:
            if self.xaxis == "Binding":
                xd = self.ddict.all_data[dataname].excitation_energy - (self.ddict.all_data[dataname].xcurrent + self.ddict.all_data[dataname].shift_ke)
            elif self.xaxis == "Kinetic":
                xd = self.ddict.all_data[dataname].xcurrent + self.ddict.all_data[dataname].shift_ke
            ax.plot(xd,self.ddict.all_data[dataname].yavg,label=self.ddict.all_data[dataname].label)
        ax.legend()
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        self.canvas.draw()
       
    def clear_data(self):
        self.ddict.clear_data()
        self.datalist.clear()
        self.replot()
        
    def remove_selected(self):
        selection = self.datalist.selectedItems()
        for selecteditem in selection:
            self.ddict.remove_data(selecteditem.text())
            self.datalist.takeItem(self.datalist.indexFromItem(selecteditem).row())
            
    def normalize_left(self):
        for dataname in self.selecteddatanames:
            NormalizeLeft(self.ddict.all_data[dataname])
        self.replot()
        
    def normalize_right(self):
        for dataname in self.selecteddatanames:
            NormalizeRight(self.ddict.all_data[dataname])
        self.replot()
        
    def select_all(self):
        for n in range(self.datalist.count()):
            self.datalist.item(n).setSelected(True)
        self.get_selection()
        self.replot()
        
    def get_selection(self):
        self.selecteddatanames = []
        for selection in self.datalist.selectedItems():
            self.selecteddatanames.append(selection.text())

    def norm_max(self):
        for dataname in self.selecteddatanames:
            NormalizeMax(self.ddict.all_data[dataname])
        self.replot()
        
    def revert(self):
        for dataname in self.selecteddatanames:
            self.ddict.all_data[dataname]._revert_data()
        self.replot()
        
    def subline_left(self):
        for dataname in self.selecteddatanames:
            SubtractLineLeft(self.ddict.all_data[dataname])
        self.replot()
        
    def subline_right(self):
        for dataname in self.selecteddatanames:
            SubtractLineRight(self.ddict.all_data[dataname])
        self.replot()
        
    def norm_min_max(self):
        for dataname in self.selecteddatanames:
            NormalizeMinMax(self.ddict.all_data[dataname])
        self.replot()
        
    def plot_multicolumn(self):
        self.get_selection()
        if len(self.selecteddatanames) != 1:
            self.raise_error("'Plot Columns' can only plot from a single file.  Please select one file and try again!")
            return
        dataname = self.selecteddatanames[0]
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        if self.xaxis == "Binding":
            self.xlabel = "Binding Energy (eV)"
            ax.invert_xaxis()
        elif self.xaxis == "Kinetic":
            self.xlabel = "Kinetic Energy (eV)"
        for n in range(self.ddict.all_data[dataname].n_col):
            if self.xaxis == "Binding":
                xd = self.ddict.all_data[dataname].excitation_energy - (self.ddict.all_data[dataname].xcurrent + self.ddict.all_data[dataname].shift_ke)
            elif self.xaxis == "Kinetic":
                xd = self.ddict.all_data[dataname].xcurrent + self.ddict.all_data[dataname].shift_ke
            ax.plot(xd,self.ddict.all_data[dataname].ycurrent[:,n],label=str('sweep '+str(n)))
       #ax.legend()
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        self.canvas.draw()
    
    def raise_error(self,message):
        error_dialog = QMessageBox()
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error!")
        error_dialog.exec_()
    
    def plot_BE(self):
        self.xaxis = "Binding"

    def plot_KE(self):
        self.xaxis = "Kinetic"
        
    def export_data(self):
        #assumes data plotted; i.e. get_selection has been done before
        if len(self.selecteddatanames) == 0:
            self.raise_error("No Data Selected.  Try clicking 'Plot Selected' first.")
            return
        savefilebase = QFileDialog.getSaveFileName(self,'Enter Base Name for Save Files')[0]
        if savefilebase == "":
            return
        for dataname in self.selecteddatanames:
            outputfilename = savefilebase+self.ddict.all_data[dataname].label+".dat"
            xd = self.ddict.all_data[dataname].xcurrent + self.ddict.all_data[dataname].shift_ke
            yd = self.ddict.all_data[dataname].yavg
            od = np.column_stack((xd,yd))
            np.savetxt(outputfilename,od)
            
    def show_metadata(self):
        self.get_selection()
        for dataname in self.selecteddatanames:
            self.raise_md_window(self.ddict.all_data[dataname])
        
    def raise_md_window(self,data_object):
        def save_md():
            data_object.excitation_energy = float(hventry.text())
            data_object.shift_ke = float(shiftentry.text())
            data_object.label = labelentry.text()
            data_object.multiplier = float(multentry.text())
            data_object._sum_ydata()            
            mdwindow.accept()
        def close_md():
            mdwindow.accept()
        mdwindow = QDialog()
        mdwindow.setWindowTitle(data_object.name)
        labellabel = QLabel("Label")
        labelentry = QLineEdit(data_object.label)
        hvlabel = QLabel("Excitation Energy")
        hventry = QLineEdit(str(data_object.excitation_energy))
        commentlabel = QLabel("Comments")
        commenttext = QLabel(data_object.comment)
        shiftlabel = QLabel("KE Shift (eV)")
        shiftentry = QLineEdit(str(data_object.shift_ke))
        okaybutton = QPushButton("Save Changes")
        okaybutton.clicked.connect(lambda: save_md())
        cancelbutton = QPushButton("Close")
        cancelbutton.clicked.connect(lambda: close_md())
        nsweeplabel = QLabel("Number of Sweeps")
        nsweeptext = QLabel(str(data_object.n_sweeps))
        multlabel = QLabel("Multiplier")
        multentry = QLineEdit(str(data_object.multiplier))
        mdlayout = QGridLayout()
        mdlayout.addWidget(labellabel,1,1)
        mdlayout.addWidget(labelentry,1,2)
        mdlayout.addWidget(hvlabel,2,1)
        mdlayout.addWidget(hventry,2,2)
        mdlayout.addWidget(shiftlabel,3,1)
        mdlayout.addWidget(shiftentry,3,2)
        mdlayout.addWidget(nsweeplabel,4,1)
        mdlayout.addWidget(nsweeptext,4,2)
        mdlayout.addWidget(multlabel,5,1)
        mdlayout.addWidget(multentry,5,2)
        mdlayout.addWidget(commentlabel,6,1)
        mdlayout.addWidget(commenttext,6,2)
        mdlayout.addWidget(okaybutton,7,1)
        mdlayout.addWidget(cancelbutton,7,2)
        mdwindow.setLayout(mdlayout)
        mdwindow.exec_()
        
    def autoshift(self):
        if len(self.selecteddatanames) == 0:
            return
        def close_shift():
            shiftwindow.accept()
        def do_shift():
            targetval = float(valentry.text())
            for dataname in self.selecteddatanames:
                ShiftToValue(self.ddict.all_data[dataname],targetval,self.xaxis)
            self.replot()
        shiftwindow = QDialog()
        shiftwindow.setWindowTitle("Enter Desired Value")
        if self.xaxis == "Binding":
            vallabel = QLabel("Desired Binding Energy:")
        elif self.xaxis == "Kinetic":
            vallabel = QLabel("Desired Kinetic Energy:")
        valentry = QLineEdit()
        shiftbutton = QPushButton("Accept")
        shiftbutton.clicked.connect(lambda: do_shift())
        cancelbutton = QPushButton("Close")
        cancelbutton.clicked.connect(lambda: close_shift())
        shiftlayout = QHBoxLayout()
        shiftlayout.addWidget(vallabel)
        shiftlayout.addWidget(valentry)
        shiftlayout.addWidget(shiftbutton)
        shiftlayout.addWidget(cancelbutton)
        shiftwindow.setLayout(shiftlayout)
        shiftwindow.exec_()
        
        

        
if __name__ == "__main__":
     app = QApplication(sys.argv)
     main = PeakPlottingProgramMain()
     main.show()
     sys.exit(app.exec_())
