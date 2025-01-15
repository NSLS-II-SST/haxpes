from haxpes.xpswriter import write_xps_file

def export_from_queue():
    fqueue = "./LiveQueue.txt"
    qobj = open(fqueue,'r')
    l = qobj.readlines()
    for line in l:
        if line[0] != "#":
            uid = line[:-1]
            write_xps_file(uid)

    qobj.close()

