import re

from numpy import column_stack, transpose
from prefect.blocks.system import Secret
from tiled.client import from_profile


def get_proposal_path(run):
    proposal = run.start.get("proposal", {}).get("proposal_id", None)
    is_commissioning = (
        "commissioning" in run.start.get("proposal", {}).get("type", "").lower()
    )
    cycle = run.start.get("cycle", None)
    if proposal is None or cycle is None:
        raise ValueError("Proposal Metadata not Loaded")
    if is_commissioning:
        proposal_path = f"/nsls2/data/sst/proposals/commissioning/pass-{proposal}/"
    else:
        proposal_path = f"/nsls2/data/sst/proposals/{cycle}/pass-{proposal}/"
    return proposal_path


def get_ses_path(run):
    base_path = get_proposal_path(run)
    ses_path = base_path + "assets/haxpes-ses/"
    return ses_path


def get_md(run, md_key, default="Unknown"):
    if md_key in run.start.keys():
        return str(run.start[md_key])
    else:
        return default


def get_baseline(run, md_key, default="Unknown", firstonly=False):
    if md_key in run.baseline.data.keys():
        if firstonly:
            return str(run.baseline.data[md_key].read()[0])
        else:
            return str(run.baseline.data[md_key].read().mean())
    else:
        return default


def get_baseline_config(run, device, md_key, default="Unknown"):
    fullkey = str(device + "_" + md_key)
    if fullkey in run.baseline.config[device].keys():
        return str(run.baseline.config[device][fullkey].read()[0])
    else:
        return default


def get_photon_energy(run, default=0):
    if "beam_selection" in run.baseline.data.keys():
        beamselect = run.baseline.data["beam_selection"].read()[0]
        if beamselect == "Tender":
            en = round(run.baseline.data["SST2 Energy_energy"].read().mean(), 1)
        elif beamselect == "Soft":
            en = round(run.baseline.data["en_energy"].read().mean(), 1)
        else:
            en = default
    else:
        en = default
    return str(en)


def get_scantype(run):
    if "scantype" in run.start.keys():
        return run.start["scantype"]
    else:
        return None


def get_general_metadata(run):

    metadata = get_mono_md(run)

    try:
        metadata["Proposal"] = str(run.start["proposal"]["proposal_id"])
    except:
        metadata["Proposal"] = unknown

    metadata["UID"] = get_md(run, "uid")
    metadata["Start Date/Time"] = get_md(run, "start_datetime")
    metadata["Scan ID"] = get_md(run, "scan_id")
    metadata["SAF"] = get_md(run, "saf")
    metadata["Sample Name"] = get_md(run, "sample_name")
    metadata["Sample Description"] = get_md(run, "sample_desc")
    #    metadata['Mono Crystal'] = get_baseline_config(run,'SST2 Energy','mono_crystal')
    #    metadata['Undulator Harmonic'] = get_baseline_config(run,'SST2 Energy','harmonic')
    metadata["Comment"] = get_md(run, "comment")

    if len(run.start["hints"]["dimensions"]) == 1:
        if len(run.start["hints"]["dimensions"][0][0]) == 1:
            x_key = run.start["hints"]["dimensions"][0][0][0]
    else:
        x_key = "I dunno"
    metadata["X Label"] = x_key

    metadata["Detectors"] = get_md(run, "detectors")

    metadata["FloodGun Energy"] = get_baseline_config(run, "FloodGun", "energy")
    metadata["FloodGun Emission"] = get_baseline_config(run, "FloodGun", "Iemis")
    metadata["FloodGun Grid Voltage"] = get_baseline_config(run, "FloodGun", "Vgrid")

    metadata["L1 Stripe"] = get_baseline(run, "L1_stripe", firstonly=True)
    metadata["L2 Mirror"] = get_baseline(run, "L2_mirror_type", firstonly=True)
    metadata["L2 Stripe"] = get_baseline(run, "L2_stripe", firstonly=True)

    metadata["HSlit Gap"] = get_baseline(run, "HAXPES slits_hsize")
    metadata["HSlit Center"] = get_baseline(run, "HAXPES slits_hcenter")
    metadata["VSlit Gap"] = get_baseline(run, "HAXPES slits_vsize")
    metadata["VSlit Center"] = get_baseline(run, "HAXPES slits_vcenter")
    metadata["Sample X"] = get_baseline(run, "haxpes_manipulator_x")
    metadata["Sample Y"] = get_baseline(run, "haxpes_manipulator_y")
    metadata["Sample Z"] = get_baseline(run, "haxpes_manipulator_z")
    metadata["Sample Rotation"] = get_baseline(run, "haxpes_manipulator_r")

    return metadata


def get_metadata_xps(run):

    metadata = get_general_metadata(run)

    try:
        peak_config = run.primary.descriptors[0]["configuration"]["PeakAnalyzer"][
            "data"
        ]
        for peakkey in peak_config.keys():
            out_key = peakkey.replace("_", " ")
            metadata[out_key] = str(peak_config[peakkey])
    except KeyError:
        metadata["Peak Analyzer"] = "Not Used"

    metadata["I0 Integration Time"] = str(
        run.primary.descriptors[0]["configuration"]["I0 ADC"]["data"][
            "I0 ADC_exposure_time"
        ]
    )
    metadata["I0 Data"] = str(run.primary.read()["I0 ADC"].data)

    metadata["Excitation Energy"] = get_photon_energy(run)

    metadata["Number of Sweeps"] = get_md(run, "sweeps")

    return metadata


def get_data_xps(run):

    energy_axis = run.primary.read()["PeakAnalyzer_xaxis"].data[0, :]
    imdat = run.primary.read()["PeakAnalyzer_edc"].data

    # add dimension mode should be a metadata key.  If true, keep every sweep individually.  For now force False
    add_dimension = False
    if add_dimension:
        edc = transpose(imdat)
    else:
        edc = imdat.sum(axis=0)

    data_array = column_stack((energy_axis, edc))

    return data_array


def get_mono_md(run):
    """
    checks if SST-1 or SST-2, then gets correct md.
    if beamselect is not in md, returns nothing
    """
    metadata = {}

    if "beam_selection" in run.baseline.data.keys():
        beamselect = run.baseline.data["beam_selection"].read()[0]
        if beamselect == "Tender":
            metadata["Mono Crystal"] = get_baseline_config(
                run, "SST2 Energy", "mono_crystal"
            )
            metadata["Undulator Harmonic"] = get_baseline_config(
                run, "SST2 Energy", "harmonic"
            )
            metadata["Filter Position"] = get_baseline(run, "nBPM Filter")
        elif beamselect == "Soft":
            metadata["CFF"] = get_baseline_config(run, "en", "monoen_cff")
            metadata["Grating"] = get_baseline_config(
                run, "en", "monoen_gratingx_setpoint"
            )
            metadata["Mirror2"] = get_baseline_config(
                run, "en", "monoen_mirror2x_setpoint"
            )
            metadata["Undulator Harmonic"] = get_baseline_config(run, "en", "harmonic")
            metadata["Exit Slit Gap"] = get_baseline(run, "Exit Slit AB")
    return metadata


def make_header(metadata, datatype, detlist=None):
    """
    compiles metadata into a header for data export.  Datatype should be "xps" or "xas"
    """

    header = ""
    for k in metadata.keys():
        header = header + k + ": " + metadata[k] + "\n"

    if datatype == "xps":
        header = header + "\n"
        header = header + "[Data]\n"
        header = header + "Energy"
        for n in range(int(metadata["Number of Sweeps"])):
            header = header + ", Dimension" + str(n)
        header = header + "\n"
    elif datatype == "xas":
        header = header + "\n"
        header = header + "-----------------------------------------\n"
        header = header + "Energy"
        if detlist != None:
            for det in detlist:
                header = header + ", " + det.replace(" ", "_")
        header = header + "\n"
    elif datatype == "generic":
        header = header + "\n"
        header = header + "-----------------------------------------\n"
        header = header + metadata["X Label"].replace(" ", "_")
        if detlist != None:
            for det in detlist:
                header = header + ", " + det.replace(" ", "_")
        header = header + "\n"

    else:
        pass

    return header


def write_header_only(fpath, header):
    fobj = open(fpath, "w")
    fobj.write(header)
    fobj.close()

def get_xas_data(run):
    """
    returns data array 
    """
    #first check if soft or tender data:
    if 'beam_selection' in run.baseline.data.keys():
        beamselect = run.baseline.data['beam_selection'].read()[0]
        if beamselect == "Soft":
            energy_key = 'en_energy'
        else:
            energy_key = 'SST2 Energy_energy'
    else:   #for now, if beam_selection is not in data, just assume tender
        energy_key = 'SST2 Energy_energy'

    data_array = run.primary.read()[energy_key].data

    detlist = run.start["detectors"]
    for det in detlist:
        if det == "PeakAnalyzer":
            data_array = column_stack(
                (data_array, run.primary.read()["PeakAnalyzer_total_counts"].data)
            )
        else:
            data_array = column_stack((data_array, run.primary.read()[det].data))
    return data_array


def get_generic_1d_data(run):
    if len(run.start["hints"]["dimensions"]) == 1:
        if len(run.start["hints"]["dimensions"][0][0]) == 1:
            x_key = run.start["hints"]["dimensions"][0][0][0]
    else:
        return  # I don't know what to do

    data_array = run.primary.read()[x_key].data

    detlist = run.start["detectors"]
    for det in detlist:
        if det == "PeakAnalyzer":
            data_array = column_stack(
                (data_array, run.primary.read()["PeakAnalyzer_total_counts"].data)
            )
        else:
            data_array = column_stack((data_array, run.primary.read()[det].data))

    return data_array


def initialize_tiled_client(beamline_acronym):
    return from_profile("nsls2")[beamline_acronym]["raw"]


def generate_file_name(run, extension):
    """generates a file name from the metadata in the run.
    If no export filename or sample name is given, filename will be Scan_<ScanID>.
    """
    S = ""
    if "export_filename" in run.start.keys() and run.start["export_filename"]:
        S = S + run.start["export_filename"]
    elif "sample_name" in run.start.keys():
        S = S + run.start["sample_name"]
    S = sanitize_filename(S)
    if S == "":
        S = "Scan"

    # would be nice to have photon energy for XPS, but don't know how to make that work for both soft and tender yet
    N = run.start["scan_id"]

    if "scantype" in run.start.keys() and run.start["scantype"] == "xps":
        EC = "_"
        en = get_photon_energy(run)
        if en != "0":
            EC = EC + f"{en}eV_"
        cl = get_md(run, "core_line")
        if cl != "Unknown":
            EC = EC + f"{cl}"
    elif "scantype" in run.start.keys() and run.start["scantype"] == "xas":
        cl = get_md(run, "edge")
        EC = f"_{cl}"
    else:
        EC = ""

    if extension[0] == ".":
        extension = extension[1:]

    fn = f"{S}{EC}_{N}.{extension}"
    return fn


def sanitize_filename(filename):
    """
    Sanitize a filename by removing/replacing invalid characters. Avoids wrecking
    either Windows or Linux paths.

    Eliminates any characters that aren't alphanumeric, period, hyphen, underscore, forward slash, colon, or backslash
    Replaces multiple hyphens with a single hyphen
    Replaces whitespace and multiple underscores with a single underscore

    Parameters
    ----------
    filename : str
        The filename to sanitize

    Returns
    -------
    str
        The sanitized filename with invalid characters removed/replaced
    """
    # Replace any characters that aren't alphanumeric, period, hyphen, underscore, forward slash, colon, or backslash
    filename = re.sub(r"[^\w\s\-\./:\\]", "", filename)
    # Replace multiple hyphens with single hyphen
    filename = re.sub(r"-+", "-", filename)
    # Replace whitespace and multiple underscores with single underscore
    filename = re.sub(r"[_\s]+", "_", filename)
    return filename


def get_resPES_data(run):
    data_dictionary = {}

    metadata = get_general_metadata(run)
    try:
        peak_config = run.primary.descriptors[0]["configuration"]["PeakAnalyzer"][
            "data"
        ]
        for peakkey in peak_config.keys():
            out_key = peakkey.replace("_", " ")
            metadata[out_key] = str(peak_config[peakkey])
    except KeyError:
        metadata["Peak Analyzer"] = "Not Used"
    metadata["I0 Integration Time"] = str(
        run.primary.descriptors[0]["configuration"]["I0 ADC"]["data"][
            "I0 ADC_exposure_time"
        ]
    )

    data_dictionary["Metadata"] = metadata

    if "shape" not in run.start.keys():
        return data_dictionary  # just give up ...
    if "PeakAnalyzer" not in run.start["detectors"]:
        return data_dictionary  # like I said ...

    beam_type = run.baseline.config["beam_selection"]["beam_selection"].read()[0]
    if beam_type == "Tender":
        en_key = "SST2 Energy_energy"
    elif beam_type == "Soft":
        en_key = "en_energy"  ### check this !!!
    else:
        return data_dictionary  # again, just give up ...

    n_hv = run.start["shape"][0]
    n_sweep = run.start["shape"][1]

    n_KE = run.primary.read()["PeakAnalyzer_xaxis"].data.shape[1]

    hv = run.primary.read()[en_key].data.reshape(n_hv, n_sweep)
    hv = hv.mean(axis=1)

    sweep = run.primary.read()["Exposure"].data.reshape(
        n_hv, n_sweep
    )  # check motor name
    sweep = sweep.mean(axis=0)

    KE = run.primary.read()["PeakAnalyzer_xaxis"].data.reshape(n_hv, n_sweep, n_KE)
    KE = KE.mean(axis=(0, 1))

    edc = run.primary.read()["PeakAnalyzer_edc"].data.reshape(n_hv, n_sweep, n_KE)
    edc = edc.mean(axis=1)
    edc_norm = empty(edc.shape)
    for n in range(n_hv):
        edc_norm[n, :] = edc[n, :] / edc[n, -20:].mean()

    DataSets = {"edc_raw": edc, "edc_norm": edc_norm}

    data_dictionary["DataSets"] = DataSets

    signals = {}
    for det in run.start["detectors"]:
        if det != "PeakAnalyzer":
            detdat = run.primary.read()[det].data.reshape(n_hv, n_sweep)
            detdat = detdat.mean(axis=1)
            signals[det] = detdat

    AEY = run.primary.read()["PeakAnalyzer_total_counts"].data.reshape(n_hv, n_sweep)
    AEY = AEY.mean(axis=1)
    signals["AugerYield"] = AEY

    data_dictionary["Signals"] = signals

    axes = {"Photon Energy": hv, "Kinetic Energy": KE}

    data_dictionary["Axes"] = axes

    return data_dictionary
