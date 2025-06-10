import numpy as np

def bounds_to_list(scan_bounds):
    """converts list of scan bounds from format start_0, stop_0, step_0, step_1, step_1, stop_2, step_2 ... to list"""

    n_reg = int((len(scan_bounds) - 1)/2)

    full_list = np.arange(scan_bounds[0],scan_bounds[1],scan_bounds[2])

    for n in range(1, n_reg):
        region_list = np.arange(scan_bounds[2*n-1],scan_bounds[2*n+1],scan_bounds[2*n+2])
        full_list = np.concatenate((full_list,region_list))

    full_list = full_list.tolist()

    return full_list


def bounds_to_dict_list(scan_bounds,key_name):

    scan_list = bounds_to_list(scan_bounds)

    dict_list = []
    for n in range(len(scan_list)):
        dict_list.append({key_name: scan_list[n]})

    return dict_list
