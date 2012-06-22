import numpy
import scipy.fftpack as fftpack
import scipy.signal as signal
import math
import const
import sys

NA = numpy.newaxis
pi = math.pi

###########################################################
#ALL in one method for W99 space-time analisis class
###########################################################
class WK99spectrum:
    def __init__(self, datain, spd, nDayWin, nDaySkip, tim_taper=0.1, ifmask=True,\
                 rawsmooth=1):
        """space-time spectram WK99
        
        Arcuments:
        
        'datain'   -- analysis array. dimension must be (lon,lat,...,time).
                      causion!! 
                       - meridional components is symetric against equator
                       - longitudinal component is cubic
    
        'spd'      -- samples per day
    
        'ndaywin'  -- days of window elements size
       
        'ndayskip' -- days of lag. negative means there will be overlap segments
       
        'dim'      -- dimension for (time, lat, lon)
    
        'tim_taper'-- tapering range tim_taper*TotalTimeSample

        'rawsmooth' -- number of 1-2-1 smoothin for wavenumber & frequency direction to raw spectrum.

        'backsmooth' -- 
        """

        ntim, nlat, nlon = datain.shape
    
        nDayTot   = ntim/spd     # days of input variable
        nSampTot  = nDayTot*spd  # samples of total input variable
        nSampWin  = nDayWin*spd  # samples of per temporal window
        nSampSkip = nDaySkip*spd # samples to skip between window segments
        nWindow = (nSampTot - nSampWin)/(nSampWin + nSampSkip) + 1

        #remove annual cycle(The first three harmonics of seasonal cycle removed)
        if (nDayTot >= 365/3):
            rf = fftpack.rfft(datain,axis=0)
            freq = fftpack.rfftfreq(nSampWin, d=1./float(spd))
            rf[(freq <= 3./365) & (freq >=1./365),:,:] = 0.0     #freq<=3./365 only??
            datain = fftpack.irfft(rf,axis=0)

        #decompose sym and antisym componet. NH is symmetric
        symm = 0.5*(datain[:,:nlat/2+1,:] + datain[:,nlat:nlat/2-1:-1,:])  
        anti = 0.5*(datain[:,:nlat/2,:] - datain[:,nlat:nlat/2:-1,:]) 
        datain = numpy.concatenate([anti, symm],axis=1)

        sumpower = numpy.zeros((nSampWin,nlat,nlon))
        ntstrt = 0
        ntlast = nSampWin

        for i in range(nWindow):
            data = datain[ntstrt:ntlast,:,:]  

            # - remove dominant signals ---------------------------------------------
            # mean & linear trend removed
            #------------------------------------------------------------------------
            data = signal.detrend(data,axis=0)
            #- terpaing -------------------------------------------------------------
            # multipling window function to taper segments to zero
            #------------------------------------------------------------------------
            if tim_taper != 0:
                tp = int(nSampWin*tim_taper)
                window = numpy.ones(nSampWin)
                x = numpy.arange(tp)
                window[:tp] = 0.5*(1.0-numpy.cos(x*pi/tp))
                window[-tp:] = 0.5*(1.0-numpy.cos(x[::-1]*pi/tp))
                data = data * window[:,NA,NA]

#            data = data * signal.hann(nSampWin)[:,NA,NA]

            #- computing space-time spectrum -----------------------------------------
            # 2d complex FFT & nomarized & sort in ascendig order
            #-------------------------------------------------------------------------
            # CAUTION!
            # scipy.fftpack.fft's formula is
            #     f(x) = sum_k c(k)+exp(-i*k*x)
            # so wave is rebresented by exp(i(-k*x-omega*t)). In this case, 
            # if frequency positive, negative wavenumber means eastward, positive frequency 
            # means westward.
            
            power = fftpack.fft2(data,axes=(0,2))/nlon/nSampWin  #normalized by sample size
            sumpower = sumpower + numpy.abs(power)**2

            ntstrt = ntlast + nSampSkip
            ntlast = ntstrt + nSampWin    #loop for nSampWin

        sumpower = sumpower / nWindow

        # - sort k, f, in ascending order----------------------------------------------------------
        # This procedure sort array under matrix in each latitude
        # power = (after this procedure)
        # [0<=f<=freqmax,lat(symm is NH),kmin<=k<=kmax]
        #-------------------------------------------------------------------------------------------
        if (nlon%2 == 0):
            wavenumber = fftpack.fftshift(fftpack.fftfreq(nlon)*nlon)[1:]
            sumpower = fftpack.fftshift(sumpower,axes=2)[:,:,nlon:0:-1]
        else:
            wavenumber = fftpack.fftshift(fftpack.fftfreq(nlon)*nlon)
            sumpower = fftpack.fftshift(sumpower,axes=2)[:,:,::-1]

        frequency = fftpack.fftshift(fftpack.fftfreq(nSampWin,d=1./float(spd)))[nSampWin/2:]       
        sumpower = fftpack.fftshift(sumpower,axes=0)[nSampWin/2:,:,:]
        
        power_symm = 2.0*numpy.add.reduce(sumpower[:,nlat/2:,:],axis=1)  #NH is symm
        power_anti = 2.0*numpy.add.reduce(sumpower[:,:nlat/2,:],axis=1)  #SH is anti

        #smoothing
        for i in range(rawsmooth):
            power_symm = _smooth121_2d(power_symm)
            power_symm = _smooth121_2d(power_symm, axis=1)
            power_anti = _smooth121_2d(power_anti)
            power_anti = _smooth121_2d(power_anti, axis=1)

        ###########################################################
        # background spectrum
        ###########################################################
        background = numpy.add.reduce(sumpower, axis=1)

        freqtimes = 30               #the number of passes of filter in freqency
        stepfreq = [0.1,0.2,0.3,1.]
        wavetimes = [5, 10, 20, 40]
#        wavetimes = [10, 10, 10, 10]
#        wavetimes=[5,5,5,5]
        
        i = 1
        while i <= freqtimes:
            background[1:,:] = _smooth121_2d(background[1:,:],axis=1)
            i += 1
        m = 0
        for n in range(1,len(frequency)):
            if frequency[n] > stepfreq[m]:
                m = m + 1                
                i = 1
            while i<=wavetimes[m]:
                background[n,:] = _smooth121(background[n,:])
                i += 1

        self.wavenumber = wavenumber
        self.frequency = frequency

        if ifmask:
            power_symm = numpy.ma.array(power_symm)
            power_anti = numpy.ma.array(power_anti)
            background = numpy.ma.array(background)
            power_symm[0,:] = numpy.ma.masked
            power_anti[0,:] = numpy.ma.masked
            background[0,:] = numpy.ma.masked

        self.power_symm = power_symm
        self.power_anti = power_anti
        self.background = background
        self.sumpower = sumpower

def calcspectrum(sumpower, frequency, rawsmooth=1, freqtimes=30, stepfreq=[0.1,0.2,0.3,1.], wavetimes=[5,10,20,40], ifmask=True):
    """calculation symmetric & antisymmetric componet & background spectram

    Arguments:

       'sumpower'   -- power spcectrum array (f, lat, k). NH is antisymmetric, SH is symmetric componet
 
       'frequency'  -- frequency array

       'rawsmooth'  -- number of times to smooth along wavenumber & frequency domain

       'freqtimes'  -- smoothing times along frequency domain to calculate background

       'wavetimes'  -- smoothing times along wavenumber domain to calculate background.

       'stepfreq'   -- step frquency to change smoothing times along frequency domain to calculate background
    """

    nf, nlat, nk = sumpower.shape

    if nf != len(frequency):
        print "error! array size missmatch."
        sys.exit()

    power_symm = 2.0*numpy.add.reduce(sumpower[:,nlat/2:,:],axis=1)  #NH is symm
    power_anti = 2.0*numpy.add.reduce(sumpower[:,:nlat/2,:],axis=1)  #SH is anti

    #smoothing
    for i in range(rawsmooth):
        power_symm = _smooth121_2d(power_symm)
        power_symm = _smooth121_2d(power_symm, axis=1)
        power_anti = _smooth121_2d(power_anti)
        power_anti = _smooth121_2d(power_anti, axis=1)

    background = numpy.add.reduce(sumpower, axis=1)
    i = 1
    while i <= freqtimes:
        background[1:,:] = _smooth121_2d(background[1:,:],axis=1)
        i += 1
    m = 0
    for n in range(1,len(frequency)):
        if frequency[n] > stepfreq[m]:
            m = m + 1                
            i = 1
        while i<=wavetimes[m]:
            background[n,:] = _smooth121(background[n,:])
            i += 1

    if ifmask:
        power_symm = numpy.ma.array(power_symm)
        power_anti = numpy.ma.array(power_anti)
        background = numpy.ma.array(background)
        power_symm[0,:] = numpy.ma.masked
        power_anti[0,:] = numpy.ma.masked
        background[0,:] = numpy.ma.masked
        
    return power_symm, power_anti, background
        
def powershape(data, spd, nDayWin):
    """ return turple that represent WK99 data array.
    
    """
    ntim, nlat, nlon = data.shape
    nSampWin  = nDayWin*spd  # samples of per temporal window

    powershape = (nSampWin-nSampWin/2, nlat, nlon-(nlon+1)%2)
    
    return powershape

def genwavenumber(nlon):
    if (nlon%2 == 0):
        wavenumber = fftpack.fftshift(fftpack.fftfreq(nlon)*nlon)[1:]
    else:
        wavenumber = fftpack.fftshift(fftpack.fftfreq(nlon)*nlon)

    return wavenumber

def genfrequency(spd, nDayWin):
    """return freqency array. units is cpd (Cycle per Day)

    Arguments:

       'nDayWin' -- number of days per one segment

       'spd'     -- number of samples per one day 
    """
    nSampWin = nDayWin*spd
    if (nSampWin%2 == 0):
        frequency = fftpack.fftfreq(nSampWin,d=1./float(spd))[:nSampWin/2]       
    else:
        frequency = fftpack.fftfreq(nSampWin,d=1./float(spd))[:nSampWin/2+1]       

    return frequency

def decompose_antisymm(datain):
    """decompose sym and antisym component
    """
    nlat = datain.shape[1]
    symm = 0.5*(datain[:,:nlat/2+1,:] + datain[:,nlat:nlat/2-1:-1,:])  
    anti = 0.5*(datain[:,:nlat/2,:] - datain[:,nlat:nlat/2:-1,:]) 

    return numpy.concatenate([anti, symm],axis=1)


def _smooth121(array):
    #smoothin by moving average with weight (1,2,1)
    #if array.ndim != 1:
    #    print "ERROR!! smooth_121:: input array must be 1-D"
    #    exit

    weight = numpy.array([1.,2.,1.])/4.0

    return numpy.convolve(numpy.r_[array[0],array,array[-1]],weight,'valid')

def _smooth121_2d(array,axis=1):
    w = numpy.array([[0,0,0],[1,2,1],[0,0,0]])/4.0
    if (axis==0):
        w = w.T
    return signal.convolve2d(array, w, 'same','symm')


    
