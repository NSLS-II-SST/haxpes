from .hax_suspenders import suspend_psh1, suspend_psh2, suspend_psh4, suspend_psh5, suspend_FEsh1, suspend_beamstat
from .hax_runner import RE
from .hax_hw import softbeamenable, beamselection


def enable_soft_beam():
    if beamselection.get() != "none":
        print("Stopping.  "+beamselection.get()+" beam enabled.  Disable first.")
        return 0
    if softbeamenable.get() != "HAXPES":
        print("HAXPES endstation not selected for soft beam.  Cannot enable.")
        return 0
    beamselection.set("Soft")
    RE.install_suspender(suspend_psh4)
    RE.install_suspender(suspend_psh5)
    import IPython
    from haxpes.energy_soft import ensoft, polsoft, hsoft, monosoft
    ip = IPython.get_ipython()
    ip.user_global_ns['en'] = ensoft
    ip.user_global_ns['pol'] = polsoft
    ip.user_global_ns['h'] = hsoft
    ip.user_global_ns['mono'] = monosoft
    

def enable_tender_beam():
    if beamselection.get() != "none":
        print("Stopping.  "+beamselection.get()+" beam enabled.  Disable first.")
        return 0
    beamselection.set("Tender")
    RE.install_suspender(suspend_psh1)
   #RE.install_suspender(suspend_psh2)
    from .energy_tender import mono,en,h,U42
    U42.tolerance.set(1)
    import IPython
    ip = IPython.get_ipython()
    ip.user_global_ns['en'] = en
    ip.user_global_ns['h'] = h
    ip.user_global_ns['mono'] = mono
    ip.user_global_ns['U42'] = U42

def disable_soft_beam():
    if beamselection.get() != "Soft":
        print("Stopping.  Soft beam not enabled.  Currently "+beamselection.get()+" is enabled.")
        return 0
    beamselection.set("none")
    RE.remove_suspender(suspend_psh4)
    RE.remove_suspender(suspend_psh5)
    import IPython
    ip = IPython.get_ipython()
    ip.user_global_ns.pop('en', None)
    ip.user_global_ns.pop('pol', None)
    ip.user_global_ns.pop('h', None)
    ip.user_global_ns.pop('mono', None)

def disable_tender_beam(): 
    if beamselection.get() != "Tender":
        print("Stopping.  Tender beam not enabled.  Currently "+beamselection.get()+" is enabled.")
        return 0
    beamselection.set("none")
    RE.remove_suspender(suspend_psh1)
    RE.remove_suspender(suspend_psh2)
    import IPython
    ip = IPython.get_ipython()
    ip.user_global_ns.pop('en', None)
    ip.user_global_ns.pop('h', None)
    ip.user_global_ns.pop('mono', None)
    ip.user_global_ns.pop('U42', None)

def enable_both_beams():
    if beamselection.get() != "none":
        print("Stopping.  "+beamselection.get()+" beam enabled.  Disable first.")
        return 0
    if softenable.get() != "HAXPES":
        print("HAXPES endstation not selected for soft beam.  Cannot enable.")
        return 0
    beamselection.set("Soft & Tender")
    RE.install_suspender(suspend_psh4)
    RE.install_suspender(suspend_psh5)
    RE.install_suspender(suspend_psh1)
    #RE.install_suspender(suspend_psh2)
    from .energy_tender import mono,en,h,U42
    U42.tolerance.set(1)
    import IPython
    ip = IPython.get_ipython()
    ip.user_global_ns['en_t'] = en
    ip.user_global_ns['h_t'] = h
    ip.user_global_ns['mono_t'] = mono
    ip.user_global_ns['U42'] = U42
    from haxpes.energy_soft import ensoft, polsoft, hsoft, monosoft
    ip.user_global_ns['en_s'] = ensoft
    ip.user_global_ns['pol_s'] = polsoft
    ip.user_global_ns['h_s'] = hsoft
    ip.user_global_ns['mono_s'] = monosoft
    


def disable_both_beams():
    if beamelection.get() != "Soft & Tender":
        print("Stopping.  Soft & Tender beams not enabled.  Currently "+beamselection.get()+" is enabled.")
        return 0
    beamselection.set("none")
    RE.remove_suspender(suspend_psh4)
    RE.remove_suspender(suspend_psh5)
    RE.remove_suspender(suspend_psh1)
    RE.remove_suspender(suspend_psh2)
    import IPython
    ip = IPython.get_ipython()
    ip.user_global_ns.pop('en_t', None)
    ip.user_global_ns.pop('h_t', None)
    ip.user_global_ns.pop('mono_t', None)
    ip.user_global_ns.pop('U42', None)
    ip.user_global_ns.pop('en_s', None)
    ip.user_global_ns.pop('pol_s', None)
    ip.user_global_ns.pop('h_s', None)
    ip.user_global_ns.pop('mono_s', None)

def enable_test_mode():
    if beamselection.get() != "none":
        print("Stopping.  "+beamselection.get()+" beam enabled.  Disable first.")
        return 0
    beamselection.set("testing")
    RE.remove_suspender(suspend_FEsh1)
    RE.remove_suspender(suspend_beamstat)

def disable_test_mode():
    if beamselection.get() != "testing":
        print("Stopping.  "+beamselection.get()+" beam enabled.  Disable first.")
        return 0
    beamselection.set("none")
    RE.install_suspender(suspend_FEsh1)
    RE.install_suspender(suspend_beamstat)
