from nbs_bl.hw import I0
from nbs_bl.plans.scans import nbs_count, nbs_list_grid_scan
from nbs_bl.utils import merge_func
from nbs_bl.help import add_to_scan_list, add_to_func_list, _add_to_import_list
from nbs_bl.plans.plan_stubs import set_exposure
from nbs_bl.plans.scan_decorators import wrap_scantype
from nbs_bl.plans.preprocessors import wrap_metadata
#from bluesky.preprocessors import suspend_decorator
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
from nbs_bl.queueserver import GLOBAL_USER_STATUS
#from haxpes.hax_suspenders import suspendHAX_tender

from pandas import read_excel

from os.path import splitext


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

default_dwell_time = 0.1
default_lens_mode = "Angular"
default_acq_mode = "Image"

detector_widths = {"500": 40.0, "200": 16.0, "100": 8.0, "50": 4.0, "20": 1.6}

GLOBAL_XPS_PLANS = GLOBAL_USER_STATUS.request_status_dict("XPS_PLANS", use_redis=True)
GLOBAL_XPS_PLANS.clear()


def add_to_xps_list(f, key, **plan_info):
    """
    A function decorator that will add the plan to the built-in list
    """
    _add_to_import_list(f, "xps")
    GLOBAL_XPS_PLANS[key] = {}
    GLOBAL_XPS_PLANS[key].update(plan_info)
    return f


def estimate_time(region_dictionary, analyzer_settings, number_of_sweeps):
    if "dwell_time" in analyzer_settings.keys():
        dwelltime = analyzer_settings["dwell_time"]
    else:
        dwelltime = default_dwell_time
    num_points = (
        region_dictionary["energy_width"]
        + detector_widths[str(analyzer_settings["pass_energy"])]
    ) / region_dictionary["energy_step"]
    est_time = num_points * dwelltime
    total_time = est_time * number_of_sweeps
    print(
        "Estimated sweep time is "
        + str(est_time)
        + " s.  Setting I0 integration to "
        + str(est_time)
        + "."
    )
    print("Estimated total time is " + str(total_time / 60) + " min.")
    return est_time, total_time

def check_and_load(analyzer):
    if analyzer in bl.get_deferred_devices():
        analyzer = bl.load_deferred_device(analyzer)
    else:
        analyzer = bl[analyzer]
    return analyzer


def resPESscan(
    analyzer_settings,
    photon_energy_list = None,
    photon_energy_bounds = None,
    xpsPlan = None,
    region_dictionary = None,
    sweeps = 1,
    resName = "ResPES",
    md = None,
    **kwargs
    ):
    """
    Parameters
    ----------
    analyzer_settings: dictionary
        Dictionary of the analyzer settings containing "pass_energy", "dwell_time", and "lens_mode"
    photon_energy_list:  (optional) tuple or list
        List of photon energies to perform XPS scans
        Either photon_energy_list or photon_energy_bounds must be given.  If both are given, list takes priority
    photon_energy_bounds: (optional) tuple or list
        List of bounds for photon energies to perform XPS scans.  List is in format [start1, stop1, step1, stop2, step2, ...]
        Either photon_energy_list or photon_energy_bounds must be given.  If both are given, list takes priority
    xpsPlan: (optional) plan  
        The specific XPS plan to call.  One of xpsPlan or region_dictionary must be given.
        If both xpsPlan and region_dictionary are given, xpsPlan will be prioritized.
    region_dictionary: (optional) dictionary
        The XPS region dictionary to use for the XPS scans defined as pe XPS scans.
        One of xpsPlan or region_dictionary must be provided
        If both xpsPlan and region_dictionary are given, xpsPlan will be prioritized.    
    sweeps:  int or iterable
        The number of sweeps for XPS scans.  If a single int is given, the same number of sweeps will be used for each scan.
        If a list is given, len(sweeps) must be equal to len(photon_energies) and will be taken as the number of sweeps for each photon energy
    resName: name of resPES scan; will be included in metadata.  
    """
    
    #first parse inputs:
    if xpsPlan == None:
        if region_dictionary == None:
            print("Please provide either an xpsPlan or region_dictionary")
            return
        else:
            core_line = region_dictionary['region_name']
            key = f"{core_line.lower()}_xps"
            xpsPlan = _xps_factory(region_dictionary, core_line, key)
    if photon_energy_list == None:
        if photon_energy_bounds == None:
            print("Please provide either photon_energy_list or photon_energy_bounds")
            return
#        else:
#            photon_energy_list = ... #################Look up ...
    if isinstance(sweeps, int):
        _sweeps = []
        for n in range(len(photon_energy_list)):
            _sweeps.append(sweeps)
    elif all(isinstance(sweep, int) for sweep in sweeps):
        _sweeps = sweeps
    else:
        print("Sweeps must be integer or iterable of integers!")
        return

    if len(_sweeps) != len(photon_energy_list):
        print("Boo!  Number of sweeps values must be one or the same number as photon energies to scan")
        return

    global_md = bl.md
    if "scan_id" in global_md.keys():
        scan_id = global_md["scan_id"] + 1
    else:
        scan_id = ""

    md = md or {}

    _md = {
        'resPESData': True,
        'resName' : resName,
    }

    _md.update(md)

    for n in range(len(photon_energy_list)):
        photon_energy = photon_energy_list[n]
        n_sweeps = _sweeps[n]
        yield from xpsPlan(analyzer_settings,energy=photon_energy,sweeps=n_sweeps,md=_md,**kwargs)         
        



#@suspend_decorator(suspendHAX_tender)
@add_to_scan_list
@wrap_metadata({"autoexport": True})
@wrap_scantype("xps")
@merge_func(nbs_count, use_func_name=False, omit_params=["extra_dets", "dwell", "num"])
def XPSScan(
    region_dictionary,
    analyzer_settings,
    sweeps=1,
    energy=None,
    md=None,
    export_filename=None,
    **kwargs,
):
    """
    Parameters
    ----------
    region_dictionary : dict
        The region dictionary for the XPS scan, with keys "energy_center", "energy_width", "energy_step", "energy_type" and "region_name"
    analyzer_settings : dict
        The analyzer settings for the XPS scan, with keys "dwell_time", "pass_energy", "lens_mode"
    sweeps : int, optional
        The number of sweeps to perform. Default is 1.
    """
    global_md = bl.md
    if "scan_id" in global_md.keys():
        scan_id = global_md["scan_id"] + 1
    else:
        scan_id = ""

    md = md or {}  # Create an empty md dictionary if none is passed in

    analyzer_type = bl["xps_analyzer"].enum_strs[bl["xps_analyzer"].get()]

    print(f"loading {analyzer_type}")
    _md = {
        "analyzer_type": analyzer_type
    }  # _md is for local metadata that will get passed to the RunEngine
    _md["export_filename"] = export_filename
    _md["sweeps"] = sweeps

    if analyzer_type == "peak":
        analyzer = check_and_load("peak_analyzer")
        nbs_sweeps = sweeps
        ses_filename = None
    elif analyzer_type == "ses":
        analyzer = check_and_load("ses")
        nbs_sweeps = 1
        ses_filename = f"SES_{scan_id}_"

    print(f"setting up {analyzer.name}")

    _region_dictionary = region_dictionary.copy()
    if region_dictionary["energy_type"] == "binding":
        if energy is None:
            try:
                beam_energy = bl.energy.position
            except Exception as e:
                raise RuntimeError(
                    f"Cannot get energy from bl.energy.position, and Binding Energy was requested: {e}"
                )
        else:
            beam_energy = energy
        _region_dictionary["energy_center"] = (
            beam_energy - region_dictionary["energy_center"]
        )
        _region_dictionary["energy_type"] = "kinetic"

    analyzer.setup_from_dictionary(
        _region_dictionary,
        analyzer_settings,
        scan_type="XPS",
        sweeps=sweeps,
        ses_filename=ses_filename,
    )
    print("setting up I0")
    if analyzer_type == "peak":
        est_time = estimate_time(_region_dictionary, analyzer_settings, sweeps)[0]
    elif analyzer_type == "ses":
        est_time = estimate_time(_region_dictionary, analyzer_settings, sweeps)[1]
    I0initexp = I0.exposure_time.get()
    yield from set_exposure(est_time)
    print(f"run {analyzer}")
    _md.update(
        md
    )  # This ensures that metadata passed in by the user always has priority
    yield from nbs_count(
        nbs_sweeps, energy=energy, md=_md, **kwargs
    )  # think about extra dets
    print("resetting I0")
    yield from set_exposure(I0initexp)


def _xps_factory(region_dictionary, core_line, key):
    @wrap_metadata({"plan_name": key, "core_line": core_line})
    @merge_func(XPSScan, omit_params=["region_dictionary"])
    def inner(*args, **kwargs):
        """Parameters
        ----------
        repeat : int
            Number of times to repeat the scan
        **kwargs :
            Arguments to be passed to tes_gscan

        """

        yield from XPSScan(region_dictionary, *args, **kwargs)

    d = (
        f"{region_dictionary['region_name']}\n"
        + f"Perform a {region_dictionary['energy_type']} energy XPS scan for {core_line}\n"
        + f"Start: {region_dictionary['energy_center'] - region_dictionary['energy_width']/2} eV\n"
        + f"Stop: {region_dictionary['energy_center'] + region_dictionary['energy_width']/2} eV\n"
        + f"Step size: {region_dictionary['energy_step']} eV\n"
    )
    inner.__doc__ = d + inner.__doc__

    inner.__qualname__ = key
    inner.__name__ = key
    inner._short_doc = f"Do XPS for {core_line}"
    return inner



def _load_xps_toml(filename,user_ns):
    generated_plans = {}
    with open(filename, "rb") as f:
        regions = tomllib.load(f)
        for key, value in regions.items():
            name = value.get("name", key)
            energy_type = value.get("energy_type")
            energy_start = value.get("energy_start")
            energy_stop = value.get("energy_stop")
            energy_step = value.get("energy_step", 0.05)
            energy_width = abs(energy_stop - energy_start)
            energy_center = (energy_start + energy_stop) / 2
            region_name = value.get("region_name")
            core_line = value.get("core_line", "")
            region_dict = {
                "region_name": region_name,
                "energy_center": energy_center,
                "energy_width": energy_width,
                "energy_step": energy_step,
                "energy_type": energy_type,
            }
            xps_func = _xps_factory(region_dict, core_line, key)
            add_to_xps_list(
                xps_func, key, name=name, core_line=core_line, region_dict=region_dict
            )

            # Store the function
            generated_plans[key] = xps_func

            # If we're in IPython, inject into user namespace
            if user_ns is not None:
                user_ns[key] = xps_func

    return generated_plans

def _load_xps_xls(filename,user_ns):
    generated_plans = {}
    dfRegions = read_excel(filename)
    for index, row in dfRegions.iterrows():
        rdict = row.to_dict()
        energy_type = rdict["Energy Type"].lower()
        energy_start = rdict["Low Energy"]
        energy_stop = rdict["High Energy"]
        energy_step = rdict["Step Size"]
        energy_width = abs(energy_stop - energy_start)
        energy_center = (energy_start + energy_stop) / 2
        region_name = rdict["Region Name"]
        name = f"{region_name.lower().replace(' ','')}_xps"
        key = name
        core_line = rdict["Region Name"] 
        region_dict = {
            "region_name": region_name,
            "energy_center": energy_center,
            "energy_width": energy_width,
            "energy_step": energy_step,
            "energy_type": energy_type,
        }
        xps_func = _xps_factory(region_dict, core_line, key)
        add_to_xps_list(
            xps_func, key, name=name, core_line=core_line, region_dict=region_dict
        )

        # Store the function
        generated_plans[key] = xps_func

        # If we're in IPython, inject into user namespace
        if user_ns is not None:
            user_ns[key] = xps_func

    return generated_plans

@add_to_func_list
def load_xps(filename):
    """
    Load XPS plans from a TOML or Excel file and inject them into the IPython user namespace.

    Parameters
    ----------
    filename : str
        Path to the TOML or excel file containing XPS plan definitions
    """
    try:
        # Get IPython's user namespace
        ip = get_ipython()
        user_ns = ip.user_ns
    except (NameError, AttributeError):
        # Not running in IPython, just return the generated functions
        user_ns = None

    file_extension = splitext(filename)[1]
    if file_extension == ".toml":
        generated_plans = _load_xps_toml(filename,user_ns)
    elif file_extension == ".xls" or file_extension == ".XLS":
        generated_plans = _load_xps_xls(filename,user_ns)

    # Return the generated plans dictionary in case it's needed
    return generated_plans
