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
    #RE.install_suspender(suspend_psh4)
    #RE.install_suspender(suspend_psh5)
    import IPython
    from haxpes.energy_soft import ensoft, polsoft, hsoft, monosoft, epuoffset
    ip = IPython.get_ipython()
    ip.user_global_ns['en'] = ensoft
    ip.user_global_ns['pol'] = polsoft
    ip.user_global_ns['h'] = hsoft
    ip.user_global_ns['mono'] = monosoft
    ip.user_global_ns['gapoffset'] = epuoffset
    from haxpes.soft.motors import dm4, SlitAB
    ip.user_global_ns['dm4'] = dm4
    ip.user_global_ns['SlitAB'] = SlitAB
    from haxpes.soft.detectors import M4Adrain
    ip.user_global_ns['M4Adrain'] = M4Adrain
    from haxpes.soft.getbeam import transfer_setup
    ip.user_global_ns["transfer_setup"] = transfer_setup
    from haxpes.soft.soft_ops import set_photon_energy_soft, run_XPS_soft
    ip.user_global_ns["set_photon_energy"] = set_photon_energy_soft
    ip.user_global_ns["run_XPS"] = run_XPS_soft
   

def enable_tender_beam():
    if beamselection.get() != "none":
        print("Stopping.  "+beamselection.get()+" beam enabled.  Disable first.")
        return 0
    beamselection.set("Tender")
   #RE.install_suspender(suspend_psh1)
   #RE.install_suspender(suspend_psh2)
    from .energy_tender import mono,en,h,U42,gapoffset
    U42.tolerance.set(1)
    import IPython
    ip = IPython.get_ipython()
    ip.user_global_ns['en'] = en
    ip.user_global_ns['h'] = h
    ip.user_global_ns['mono'] = mono
    ip.user_global_ns['U42'] = U42
    ip.user_global_ns['gapoffset'] = gapoffset
    from haxpes.tender.tender_ops import set_photon_energy_tender, run_XPS_tender, align_beam_xps, tune_x2pitch
    ip.user_global_ns['set_photon_energy'] = set_photon_energy_tender
    ip.user_global_ns['run_XPS'] = run_XPS_tender
    ip.user_global_ns['align_beam_xps'] = align_beam_xps
    ip.user_global_ns['tune_x2pitch'] = tune_x2pitch
    from haxpes.tender.detectors import Idm1
    ip.user_global_ns['Idm1'] = Idm1
    Idm1.set_exposure(1)
    from haxpes.tender.motors import dm1, nBPM
    ip.user_global_ns['dm1'] = dm1
    ip.user_global_ns['nBPM'] = nBPM


def disable_soft_beam():
    if beamselection.get() != "Soft":
        print("Stopping.  Soft beam not enabled.  Currently "+beamselection.get()+" is enabled.")
        return 0
    beamselection.set("none")
    #RE.remove_suspender(suspend_psh4)
    #RE.remove_suspender(suspend_psh5)
    import IPython
    ip = IPython.get_ipython()
    ip.user_global_ns.pop('en', None)
    ip.user_global_ns.pop('pol', None)
    ip.user_global_ns.pop('h', None)
    ip.user_global_ns.pop('mono', None)
    ip.user_global_ns.pop('dm4', None)
    ip.user_global_ns.pop('M4Adrain',None)
    ip.user_global_ns.pop('transfer_setup',None)
    ip.user_global_ns.pop('SlitAB',None)
    ip.user_global_ns.pop('set_photon_energy',None)
    ip.user_global_ns.pop('run_XPS',None)
    ip.user_global_ns.pop('gapoffset')

def disable_tender_beam(): 
    if beamselection.get() != "Tender":
        print("Stopping.  Tender beam not enabled.  Currently "+beamselection.get()+" is enabled.")
        return 0
    beamselection.set("none")
    #RE.remove_suspender(suspend_psh1)
    #RE.remove_suspender(suspend_psh2)
    import IPython
    ip = IPython.get_ipython()
    ip.user_global_ns.pop('en', None)
    ip.user_global_ns.pop('h', None)
    ip.user_global_ns.pop('mono', None)
    ip.user_global_ns.pop('U42', None)
    ip.user_global_ns.pop('set_photon_energy',None)
    ip.user_global_ns.pop('run_XPS_tender',None)
    ip.user_global_ns.pop('align_beam_xps',None)
    ip.user_global_ns.pop('Idm1',None)
    ip.user_global_ns.pop('dm1',None)
    ip.user_global_ns.pop('nBPM',None)
    ip.user_global_ns.pop('tune_x2pitch',None)
    ip.user_global_ns.pop('run_XPS',None)
    ip.user_global_ns.pop('gapoffset')

def enable_both_beams():
    if beamselection.get() != "none":
        print("Stopping.  "+beamselection.get()+" beam enabled.  Disable first.")
        return 0
    if softbeamenable.get() != "HAXPES":
        print("HAXPES endstation not selected for soft beam.  Cannot enable.")
        return 0
    beamselection.set("Soft & Tender")
    #RE.install_suspender(suspend_psh4)
    #RE.install_suspender(suspend_psh5)
    #RE.install_suspender(suspend_psh1)
    #RE.install_suspender(suspend_psh2)
    from .energy_tender import mono,en,h,U42,gapoffset
    U42.tolerance.set(1)
    import IPython
    ip = IPython.get_ipython()
    ip.user_global_ns['en_t'] = en
    ip.user_global_ns['h_t'] = h
    ip.user_global_ns['mono_t'] = mono
    ip.user_global_ns['U42'] = U42
    ip.user_global_ns['U42offset'] = gapoffset
    from haxpes.energy_soft import ensoft, polsoft, hsoft, monosoft, epuoffset
    ip.user_global_ns['en_s'] = ensoft
    ip.user_global_ns['pol_s'] = polsoft
    ip.user_global_ns['h_s'] = hsoft
    ip.user_global_ns['mono_s'] = monosoft
    ip.user_global_ns['EPUoffset'] = epuoffset
    from haxpes.soft.motors import dm4, SlitAB
    ip.user_global_ns['dm4'] = dm4
    ip.user_global_ns['SlitAB'] = SlitAB
    from haxpes.soft.detectors import M4Adrain
    ip.user_global_ns['M4Adrain'] = M4Adrain
    from haxpes.soft.getbeam import transfer_setup
    ip.user_global_ns["transfer_setup"] = transfer_setup
    from haxpes.tender.tender_ops import set_photon_energy_tender, run_XPS_tender, align_beam_xps, tune_x2pitch
    from haxpes.soft.soft_ops import set_photon_energy_soft, run_XPS_soft
    ip.user_global_ns["set_photon_energy_soft"] = set_photon_energy_soft
    ip.user_global_ns["set_photon_energy_tender"] = set_photon_energy_tender
    ip.user_global_ns['align_beam_xps_tender'] = align_beam_xps
    ip.user_global_ns['run_XPS_soft'] = run_XPS_soft
    ip.user_global_ns['run_XPS_tender'] = run_XPS_tender
    from haxpes.tender.detectors import Idm1
    ip.user_global_ns['Idm1'] = Idm1
    Idm1.set_exposure(1)
    from haxpes.tender.motors import dm1, nBPM
    ip.user_global_ns['dm1'] = dm1
    ip.user_global_ns['nBPM'] = nBPM
    ip.user_global_ns['tune_x2picth'] = tune_x2pitch


def disable_both_beams():
    if beamselection.get() != "Soft & Tender":
        print("Stopping.  Soft & Tender beams not enabled.  Currently "+beamselection.get()+" is enabled.")
        return 0
    beamselection.set("none")
    #RE.remove_suspender(suspend_psh4)
    #RE.remove_suspender(suspend_psh5)
    #RE.remove_suspender(suspend_psh1)
    #RE.remove_suspender(suspend_psh2)
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
    ip.user_global_ns.pop('dm4', None)
    ip.user_global_ns.pop('M4Adrain',None)
    ip.user_global_ns.pop('transfer_setup',None)
    ip.user_global_ns.pop('SlitAB',None)
    ip.user_global_ns.pop('set_photon_energy_soft',None)
    ip.user_global_ns.pop('set_photon_energy_tender',None)
    ip.user_global_ns.pop('align_beam_xps_tender',None)
    ip.user_global_ns.pop('Idm1',None)
    ip.user_global_ns.pop('dm1',None)
    ip.user_global_ns.pop('nBPM',None)
    ip.user_global_ns.pop('run_XPS_tender',None)
    ip.user_global_ns.pop('run_XPS_soft',None)
    ip.user_global_ns.pop('tune_x2pitch',None)
    ip.user_global_ns.pop('EPUoffset',None)
    ip.user_global_ns.pop('U42offset',None)

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
