from haxpes.detectors import HAXDetectors
import numpy as np

def writetextfile(run,fpath):
    """ gets data and writes to filepath """

    #check plan success, record with uid
    metastr = "filename: "+fpath+"\n"
    metastr = metastr+"profile: haxpes\n"
    metastr = metastr+"uid: "+run.metadata["start"]["uid"]+"\n"
    metastr = metastr+"status: "+run.metadata["stop"]["exit_status"]+"\n"

    detectors = run.metadata["start"]["detectors"]
    
    for detname in detectors:
        for det in HAXDetectors:
            if detname == det.name:
                configkeys = list(det.read_configuration().keys())
                for key in configkeys:
                    metastr = metastr+key+": "+str(det.read_configuration()[key]['value'])+"\n"

    #get metadata, check run type.  If plan type is not "count" then get motor ...
    if run.metadata["start"]["plan_name"] != "count":
        scanaxes = run.metadata["start"]["motors"]
    else:
        scanaxes = ['time']

    metastr = metastr + "--------------------------------\n"

    #initialize data array with the first scan axis ...
    dataarray = run.primary.read()[scanaxes[0]].data
    dataarray = np.reshape(dataarray,(dataarray.shape[0],1))
    labelstr = metastr+scanaxes[0]


    #get the rest of the scan axes ... NOT TESTED!
    if len(scanaxes) >= 1:
        for ax in scanaxes[1:]:
            d = run.primary.read()[ax].data
            d = np.reshape(d,(d.shape[0],1))
            dataarray = np.hstack((dataarray,d))
            labelstr = labelstr+","+ax



    #now get the data:
    for detname in detectors:
        for det in HAXDetectors:
            if detname == det.name:
                channels = det.hints["fields"]
                for chan in channels:
                    d = run.primary.read()[chan].data
                    d = np.reshape(d,(d.shape[0],1))
                    dataarray = np.hstack((dataarray,d))
                    labelstr = labelstr+","+chan


    #write the file:
    np.savetxt(fpath,dataarray,header=labelstr,delimiter=",")
