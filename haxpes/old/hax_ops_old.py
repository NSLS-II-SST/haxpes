from .motors import sampx, sampy, sampz, sampr
from .devices.ses import ses
from bluesky.plan_stubs import abs_set, mv
from bluesky.plans import count
from .hax_hw import fs4, psh2, gv10


def set_analyzer(filename, core_line):
    """
        Defines settings for Scienta analyzer.  Relies on ses.py.  Does not start analyzer.  Must define a filename; the filename is a prefix and will have a number and extension appended to it.  Analyzer settings are delivered in a "core_line" dictionary.  Dictionary MUST contain the following keys:
        reg_name:  string name of region. Best if not too long
        center_en:  center energy (in eV Kinetic energy) of scan region.
        width:  width (in eV) of scan region
        pass_energy:  pass energy to use in eV.  Acceptable values are 20, 50, 100, and 200.
        iterations:  number of iterations.
    The following keys are optional, and will be set to default values below if they are not in dictionary:
        step_size:  size (in meV!) of energy step for region.  Default value is 50
        lens_mode: Lens mode, "Angular" or "Transmission".  Default is Angular.
        steptime:  Time per step in s.  Must be an integer multiple of 0.1 s.  Default value is 0.1 s.
        acq_mode:  Aquisition mode, "swept" or "fixed".  Default value is swept.
    """
    dstepsize = 50
    dlensmode = "Angular"
    dsteptime = 0.1
    dacqmode = "swept"
    yield from abs_set(ses.filename, filename)
    yield from abs_set(ses.region_name, core_line["reg_name"])
    yield from abs_set(ses.center_en_sp, core_line["center_en"])
    yield from abs_set(ses.width_en_sp, core_line["width"])
    yield from abs_set(ses.iterations, core_line["iterations"])
    yield from abs_set(ses.pass_en, core_line["pass_energy"])
    if "step_size" in core_line.keys():
        yield from abs_set(ses.en_step, core_line["step_size"])
    else:
        yield from abs_set(ses.en_step, dstepsize)
    if "lens_mode" in core_line.keys():
        yield from abs_set(ses.lens_mode, core_line["lens_mode"])
    else:
        yield from abs_set(ses.lens_mode, dlensmode)
    if "steptime" in core_line.keys():
        yield from abs_set(ses.steptime, core_line["steptime"])
    else:
        yield from abs_set(ses.steptime, dsteptime)
    if "acq_mode" in core_line.keys():
        yield from abs_set(ses.acq_mode, core_line["acq_mode"])
    else:
        yield from abs_set(ses.acq_mode, dacqmode)


def run_XPS_old(all_samples):
    """
        Runs samples from list "all_samples".  "all_samples" is a list of sample dictionaries.  Dictionaries MUST contain the following keys:
        x_position:  sampx position
        y_position:  sampy position
        z_position:  sampz position
        r_position:  sampr (theta) position
        cores:  list of core_line dictionaries.  See set_analyzer function for definition of core_line dictionaries.
    Sample dictionary typicall contains a sample name as well, but as yet this is not used.
    """
    for sample in all_samples:
        yield from mv(
            sampx,
            sample["x_position"],
            sampy,
            sample["y_position"],
            sampz,
            sample["z_position"],
            sampr,
            sample["r_position"],
        )
        for coreline in sample["cores"]:
            yield from set_analyzer(sample["file_name"], coreline)
            yield from fs4.open()
            yield from count([ses], 1)
            yield from fs4.close()


def run_XPS(sample_list):
    yield from psh2.open()
    yield from fs4.close()
    for i in range(sample_list.index):
        print("Moving to sample " + str(i))
        yield from sample_list.goto_sample(i)
        for region in sample_list.all_samples[i]["regions"]:
            yield from set_analyzer(sample_list.all_samples[i]["filename"], region)
            yield from psh2.open()
            yield from fs4.open()
            yield from count([ses], 1)
            yield from fs4.close()
    yield from psh2.close()


###


def withdraw_bar(heating_stage=0, close_valves=1):
    if heating_stage:
        y_out = 435
    else:
        y_out = 535
    yield from mv(sampx, 0, sampz, 0, sampr, 0)
    yield from mv(sampy, y_out)
    if close_valves:
        yield from psh2.close()
        yield from gv10.close()
        print("Please close manual valve GV9A")
