import numpy as np
import netCDF4
from dateutil import parser

NA = np.newaxis

class netcdf:
    def __init__(self,fname):
        fr = netCDF4.Dataset(fname,'r')
        vnames = fr.variables.keys()
        self.file = fr
        self.vnames = vnames
        self.lon=None
        self.lat=None
        self.lev=None
        self.time=None
        self.lonrev = False
        self.latrev = False
        for vname in vnames:
            if vname == 'lon':
                lon = fr.variables['lon']
                if lon.units == 'degrees_east':
                    self.lon = lon[:]
                elif lon.units == 'degrees_west':
#                    self.lon = lon[::-1]
                    self.lonrev = True
            if vname == 'lat':
                lat = fr.variables['lat']
                if lat.units == 'degrees_south':
                    self.lat = lat[:]
                elif lat.units == 'degrees_north':
                    self.lat = lat[:]
#                    self.lat = lat[::-1]
                    self.latrev = True
#            if vname == '':
#                lat = fr.variables['lat']
#                if lon.units == 'degrees_south':
#                    lat = lat[:]
#                elif lon.units == 'degrees_north':
#                    lat = lat[::-1]
            if vname == 'time':
                self.time = fr.variables['time']
    def read(self,vname,slon=None ,elon=None, slat=None,elat=None,slev=None,elev=None,\
                 stime=None,etime=None):
        if not(vname in self.vnames):
            print 'Error!! ' + vname + ' is not contaiend.'
            sys.exit()

        var = self.file.variables[vname]
        vardata = var[:]
        londim, latdim, levdim, timedim = (None, None, None, None)
        ndim = var.ndim
        for i, varname in enumerate(var.dimensions):
            if varname == 'lon': londim = i
            if varname == 'lat': latdim = i
            if varname == 'lev': levdim = i
            if varname == 'time': timedim = i

        mask = [None for i in range(ndim)]
        if londim != None:
            if slon == None or elon == None:
                print 'error'
                sys.exit()
            lon = self.lon
            mask[londim] = (slon <= lon) & (lon <= elon)
            self.rlon = lon[mask[londim]]
        if latdim != None:
            if slat == None or elat == None:
                print 'error'
                sys.exit()
            lat = self.lat
            mask[latdim] = (slat <= lat) & (lat <= elat)
            self.rlat = lat[mask[latdim]]
        if levdim != None:
            lev = self.lev
            if slev == None or elev == None:
                print 'error'
                sys.exit()
            mask[levdim] = (slev <= lev) & (lev <= elev)
            self.rlev = lev[mask[levdim]]
        if timedim != None:
            if stime == None or etime == None:
                print 'error'
                sys.exit()
            time = self.time
            stime = parser.parse(stime)
            etime = parser.parse(etime)
            mask[timedim] = (netCDF4.date2num(stime,time.units) <= time[:]) & \
                (time[:] <= netCDF4.date2num(etime,time.units))

        if ndim == 1:
            data = vardata[mask[0]]
        elif ndim == 2:
            data = vardata[mask[0],:]
            data = data[:,mask[1]]
        elif ndim == 3:
            data = vardata[mask[0],:,:]
            data = data[:,mask[1],:]
            data = data[:,:,mask[2]]
        elif ndim == 4:
            data = vardata[mask[0],:,:,:]
            data = data[:,mask[1],:,:]
            data = data[:,:,mask[3],:]
            data = data[:,:,:,mask[4]]

        return data

    def close(self):
        self.file.close()

