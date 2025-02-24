from export_tools import *
import numpy as np
from os import makedirs
from os.path import exists

def export_peak_xps(uid, beamline_acronym="haxpes"):

    catalog = initialize_tiled_client(beamline_acronym)
    run = catalog[uid]

    metadata = get_metadata_xps(run)
    header = make_header(metadata,"xps")
    data = get_data_xps(run)
    export_path = get_proposal_path(run)+"XPS_export/"
    #export_path = "/home/xf07id1/Documents/UserFiles/live/LiveData/XPS_export/"
    #export filename key in md ???
    if not exists(export_path):
        makedirs(export_path)
    filename = export_path+"XPS_scan"+str(run.start['scan_id'])+".csv"
    np.savetxt(filename,data,delimiter=',',header=header)

def export_xas(uid, beamline_acronym="haxpes"):
    catalog = initialize_tiled_client(beamline_acronym)
    run = catalog[uid]

    detlist = run.start['detectors']
    metadata = get_general_metadata(run)
    header = make_header(metadata,"xas",detlist=detlist)
    data = get_xas_data(run)

    export_path = get_proposal_path(run)+"XAS_export/"
    if not exists(export_path):
        makedirs(export_path)
    filename = export_path+"XAS_scan"+str(run.start['scan_id'])+".csv"
    np.savetxt(filename,data,delimiter=',',header=header)

def export_generic_1D(uid, beamline_acronym="haxpes"):
    catalog = initialize_tiled_client(beamline_acronym)
    run = catalog[uid]

    detlist = run.start['detectors']
    metadata = get_general_metadata(run)
    header = make_header(metadata,"generic",detlist=detlist)
    data = get_generic_1d_data(run)

    export_path = get_proposal_path(run)+"GeneralExport/"
    if not exists(export_path):
        makedirs(export_path)
    filename = export_path+"Scan_"+str(run.start['scan_id'])+".csv"
    np.savetxt(filename,data,delimiter=',',header=header)


def xas_export(uid, beamline_acronym="haxpes"):
    export_xas(uid,beamline_acronym)

def peak_export(uid, beamline_acronym="haxpes"):
    export_peak_xps(uid, beamline_acronym)

def generic_export(uid, beamline_acronym="haxpes"):
    export_generic_1D(uid, beamline_acronym)
