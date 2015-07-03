from astropy.io import fits
import numpy

prefix = 'ESO DRS MUSE PIXTABLE'

class Pixtable:
    def __init__(self, hdulist):
        self.hdulist = hdulist
        
    @staticmethod
    def read(fname):
        return Pixtable(fits.open(fname))

    @property
    def xpos(self):
        return self['xpos']

    @property
    def ypos(self):
        return self['ypos']

    @property
    def wavelength(self):
        return self['lambda']

    @property
    def data(self):
        return self['data']

    @property
    def stat(self):
        return self['stat']

    @property
    def dq(self):
        return self['dq']

    @property
    def origin(self):
        return self['origin']
    
    @property
    def slice(self):
        return self.origin & 0x3f

    @property
    def ifu(self):
        return (self.origin >> 6) & 0x1f

    @property
    def slice_x(self):
        return ((self.origin >> 24) & 0x7f) - 1

    @property
    def slice_y(self):
        return ((self.origin >> 11) & 0x1fff) - 1

    @property
    def exposure(self):
        exp = numpy.zeros(shape=(len(self)), dtype=numpy.int)
        try:
            nexp = self.header['{0} COMBINED'.format(prefix)]
        except KeyError:
            return exp
        for i in range(nexp):
            try:
                lo = self.header['{0} EXP{1} FIRST'.format(prefix, i+1)]
                hi = self.header['{0} EXP{1} LAST'.format(prefix, i+1)]
                exp[lo:hi + 1] = i+1
            except KeyError:
                pass
        return exp

    @property
    def header(self):
        return self.hdulist[0].header
    
    @property
    def flux_calibrated(self):
        return pt.hdulist[0].header.get('{0} FLUXCAL'.format(prefix), False)

    @property
    def sky_subtracted(self):
        return pt.hdulist[0].header.get('{0} SKYSUB'.format(prefix), False)

    def spectral_slab(self, lo, hi):
        '''Extract a new pixtable between two spectral coordinates'''
        return self[(self.wavelength >= lo) & (self.wavelength <= hi)]

    def ifu_slab(self, ifu, slc=None):
        '''Extract pixtable limited to an IFU and optionally slice'''
        return self[((self.ifu == ifu) if ifu is not None else True) &
                    ((self.slice == slc) if slc is not None else True)]

    def write(self, fname, overwrite = False):
        '''Write pixtable to a file'''
        self.hdulist.writeto(fname, clobber=overwrite)

    @property
    def columns(self):
        if isinstance(self.hdulist[1], fits.ImageHDU):
            return [ hdu.name for hdu in self.hdulist[1:] ]
        else:
            return [ col.name for col in self.hdulist[1].columns ]

    def __getitem__(self, item):
        if isinstance(item, (str, unicode)):
            if isinstance(self.hdulist[1], fits.ImageHDU):
                return self.hdulist[item].data[:,0]
            else:
                return self.hdulist[1].data[item]
        elif isinstance(item, (slice, numpy.ndarray)):
            length = len(self)
            hdulist = fits.HDUList(
                [fits.PrimaryHDU(header = self.header)]
                + [fits.ImageHDU(self[col][item].reshape(-1,1), name = col) 
                   for col in self.columns])
            return Pixtable(hdulist)
        elif isinstance(item, int):
            return dict((col, self[col][item]) for col in self.columns)

    def __len__(self):
        return len(self.xpos)

    def to_ccd(self, field = 'data', crop = False):
        '''Transfer the pixtable back to a stack of CCD images by using
        the "origin" field. Pixels outside of the slice a set to
        0. Each IFU is put to a separate extension in the output
        file. Compared with the usual 2d rebinning, this prevents
        rebinning errors.
        
        In addition to the usual data (from the 'data' field), also all
        other fields may be used here as an input.
        
        The position data is primarily taken from the pixtable header
        ("...IFU%02i SLICE%02i XOFFSET"). When this header is missing,
        a spacing is assumed from the data themself.
        '''
        ifus = list(set(self.ifu))
        ifus.sort()
        hdulist = [ fits.PrimaryHDU(header = self.header) ]
        for ifu in ifus:
            pt = self.ifu_slab(ifu)
            s = pt.slice
            x = pt.slice_x
            y = pt.slice_y
            slices=list(set(s))
            slices.sort()
            try:
                xoffsets = numpy.copy([
                        pt.header['{0} EXP0 IFU{1:02i} SLICE{2:02i} XOFFSET'
                                  .format(prefix, ifu, ss)] for ss in s
                        ])
            except KeyError:
                mx = numpy.copy([ max(x[s == ss]) - min(x[s == ss]) 
                                  for ss in slices ])
                gap = 7
                left_border = 24
                xoffsets = numpy.copy([sum(mx[:ss-slices[0]] + gap)
                                       + left_border 
                                       for ss in slices ])
            x += xoffsets[s - slices[0]]
            img = numpy.zeros(shape = (max(y) + 1, max(x) + 1))
            img[y, x] = pt[field]
            if crop:
                img = img[min(y):, min(x):]
            hdulist.append(fits.ImageHDU(img, name = 'CHAN%02i' % ifu))
        return fits.HDUList(hdulist)

