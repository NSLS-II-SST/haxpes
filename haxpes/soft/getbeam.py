from haxpes.soft.motors import M3AB, SlitAB, M4A
from bluesky.plan_stubs import mv

#first check if HAXPES is enabled.

def transfer_setup():
    #move M3 into starting place
    yield from mv(M3AB.x,-28)
    yield from mv(M3AB.y,18)
    yield from mv(M3AB.z,0)
    yield from mv(M3AB.pitch,5.64)
    yield from mv(M3AB.roll,0)
    yield from mv(M3AB.yaw,0)

    #set to some nominal energy

    #check slit positions
    yield from mv(SlitAB,75)

    #move M4A into place
    yield from mv(M4A.x, 1.95)
    yield from mv(M4A.y, -0.25)
    yield from mv(M4A.z, 0)
    yield from mv(M4A.pitch, -0.731)
    yield from mv(M4A.roll, 0)
    yield from mv(M4A.yaw, 1)

    #tweak M3 to get max drain current.

