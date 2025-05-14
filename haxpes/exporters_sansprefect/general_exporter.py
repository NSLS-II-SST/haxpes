from file_exporter import peak_export, xas_export, generic_export
from export_tools import initialize_tiled_client

def export_switchboard(uid,beamline_acronym="haxpes"):
    c = initialize_tiled_client(beamline_acronym)
    run = c[uid]
    if 'scantype' in run.start.keys():
        if run.stop['exit_status'] != "abort":
            print(run.start['autoexport'])
            if run.start['scantype'] == "xps":
                peak_export(uid)
            elif run.start['scantype'] == "xas":
                xas_export(uid)
    else:
        if run.start['autoexport']:
            generic_export(uid)
