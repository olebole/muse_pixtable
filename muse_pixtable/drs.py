import cpl

def fluxcal(pixtable, extinct_table, std_telluric, std_response, **param):
    calibrate_flux = cpl.Recipe("muse_scipost_calibrate_flux")
    calibrate_flux.calib.EXTINCT_TABLE = extinct_table
    calibrate_flux.calib.STD_TELLURIC = std_telluric
    calibrate_flux.calib.STD_RESPONSE = std_response
    res = calibrate_flux(pixtable.hdulist, param = param)
    return Pixtable(res.PIXTABLE_REDUCED)

