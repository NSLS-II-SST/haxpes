from nbs_bl.plans.time_estimation import with_repeat

default_dwell_time = 0.1
default_lens_mode = "Angular"
default_acq_mode = "Image"

detector_widths = {"500": 40.0, "200": 16.0, "100": 8.0, "50": 4.0, "20": 1.6}


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


@with_repeat
def xps_time_estimator(plan_name, plan_args, estimation_dict):
    if "region_dictionary" in plan_args:
        region_dictionary = plan_args["region_dictionary"]
    else:
        region_dictionary = estimation_dict.get("region_dictionary")
    if "analyzer_settings" in plan_args:
        analyzer_settings = plan_args["analyzer_settings"]
    else:
        analyzer_settings = estimation_dict.get("analyzer_settings")
    if "sweeps" in plan_args:
        number_of_sweeps = plan_args["sweeps"]
    else:
        number_of_sweeps = estimation_dict.get("sweeps", 1)
    est_time, total_time = estimate_time(
        region_dictionary, analyzer_settings, number_of_sweeps
    )
    return total_time
