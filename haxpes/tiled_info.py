"""
right now this is just info for how to get data.
all comments.

from tiled.client import from_profile

catalog = from_profile("haxpes")

# last run:
run = catalog[-1]

# read peak x-axis, note that the shape of the axis is (number of sweeps, x data points):

xd_all = run.primary.read()["PeakAnalyzer_xaxis"].data

# read spectra from peak, note that the shape is (number of sweeps, y data points):

yd_all = run.primary.read()["PeakAnalyzer_edc"].data


#for enregy scans ...

energy = run.primary.read()["SST2 Energy_energy"].data

I0 = run.primary.read()["I0 ADC"].data

AEY = run.primary.read()["PeakAnalyzer_total_counts"].data

#using Keithley 2600:
TEY = run.primary.read()["K2600_current"].data
"""


