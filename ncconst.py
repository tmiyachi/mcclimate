import numpy as np
from scipy.io import netcdf
import datetime
import scipy

#class Ncconst:
def createnc(fname, title=None, time=None, lev=None, lat=None, lon=None):

    f = netcdf.netcdf_file(fname, 'w')
        
    #global atrribute
    if title == None:
        title = fname
    f.title = title
    f.history = datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y') \
    + ' created by SciPy ' + scipy.version.version

    #create dimension & variables
    if lon != None:
        f.createDimension('lon', len(lon))
    
        lonvar = f.createVariable('lon', 'float32', ('lon',))
        lonvar.long_name = 'Longitude'
        lonvar.standard_name = 'longitude'
        lonvar.units = 'degrees_east'
        lonvar.axis = 'X'
        lonvar[:] = np.array(lon, dtype=np.float32)

    if lat != None:
        f.createDimension('lat', len(lat))
        
        latvar = f.createVariable('lat', 'float32', ('lat',))
        latvar.long_name = 'Latitude'
        latvar.standard_name = 'latitude'
        latvar.units = 'degrees_north'
        latvar.axis = 'Y'
        latvar[:] = np.array(lat, dtype=np.float32)

    if lev != None:
        f.createDimension('level', len(lev))
        
        levvar = f.createVariable('level', 'float32', ('level',))
        levvar.long_name = 'Level'
        levvar.units = 'hPa'
        levvar.positive = 'down'
        levvar.axis = 'Z'
        levvar[:] = np.array(lev, dtype=np.float32)

    if time != None:
        f.createDimension('time', len(time))
        timvar = f.createVariable('time', 'float64', ('time',))
        timvar.long_name = 'Time'
        timvar.standard_name = 'time'
        timvar.axis = 't'
        timvar[:] = np.array(time, np.float64)
        
    f.flush()
    return f

def createvar(ncf, varname, vararray, dims):

    vardims = []
    for dim in dims:
        if dim == x: vardims.append('lon')
        if dim == y: vardims.append('lat')
        if dim == z: vardims.append('level')
        if dim == t: vardims.append('time')

    newvar = ncf.createVariable(varname, vararray.dtype.char, vardims)
    newvar[:] = vararray

    return newvar
