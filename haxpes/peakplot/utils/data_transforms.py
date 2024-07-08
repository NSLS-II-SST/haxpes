import numpy as np

def NormalizeLeft(data_object,points=20):
    dnorm = np.mean(data_object.ycurrent[:points,:],axis=0)
    data_object.ycurrent = np.divide(data_object.ycurrent,dnorm)
    data_object._sum_ydata()
    
def NormalizeRight(data_object,points=20):
    dnorm = np.mean(data_object.ycurrent[-points:,:],axis=0)
    data_object.ycurrent = np.divide(data_object.ycurrent,dnorm)
    data_object._sum_ydata()
    
def NormalizeMax(data_object):
    maxval = np.max(data_object.ycurrent,axis=0)
    data_object.ycurrent = np.divide(data_object.ycurrent,maxval)
    data_object._sum_ydata()
    
def SubtractLineLeft(data_object,points=20):
    snorm = np.mean(data_object.ycurrent[:points,:],axis=0)
    data_object.ycurrent = data_object.ycurrent - snorm
    data_object._sum_ydata()
    
def SubtractLineRight(data_object,points=20):
    snorm = np.mean(data_object.ycurrent[-points:,:],axis=0)
    data_object.ycurrent = data_object.ycurrent - snorm
    data_object._sum_ydata()
    
def NormalizeMinMax(data_object):
    minval = np.min(data_object.ycurrent,axis=0)
    maxval = np.max(data_object.ycurrent,axis=0)
    data_object.ycurrent = np.divide((data_object.ycurrent-minval),(maxval-minval))
    data_object._sum_ydata()
    
def ShiftToValue(data_object,target_value,energy_type):
    maxindex = int(np.where(data_object.yavg == data_object.yavg.max())[0][0])
    if energy_type == "Kinetic":
        data_object.shift_ke = target_value - data_object.xcurrent[maxindex]
    elif energy_type == "Binding":
        data_object.shift_ke = data_object.excitation_energy - target_value - data_object.xcurrent[maxindex]
