import numpy as np
import netCDF4
import spharm
import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

unc = netCDF4.Dataset('uwnd.2012.nc','r')
vnc = netCDF4.Dataset('vwnd.2012.nc','r')


time = unc.variables['time']
lon = unc.variables['lon'][:]
lat = unc.variables['lat'][:]
nt = netCDF4.date2index(datetime.datetime(2012,4,1),time)
uwnd = unc.variables['uwnd'][:,10,::-1,:].mean(axis=0)
vwnd = vnc.variables['vwnd'][:,10,::-1,:].mean(axis=0)

harmonic = spharm.Spharmt(len(lon), len(lat), rsphere=6.3712e6, gridtype='gaussian', legfunc='stored')

#specdata=harmonic.gridtospec(uwnd, ntrunc=42)
#griddata=harmonic.spectogrid(specdata)
#vorspec,divspec=harmonic.getvrtdivspec(uwnd,vwnd,ntrunc=42)
#gridu, gridv = harmonic.getuv(vorspec, divspec)
strgrid, potgrid = harmonic.getpsichi(uwnd, vwnd, ntrunc=42)

unc.close()
vnc.close()

m = Basemap(projection='merc', llcrnrlat=0, urcrnrlat = 60, llcrnrlon=0, urcrnrlon=360,resolution='c')

m.drawcoastlines(linewidth=0.5)
m.drawmapboundary()

m.drawmeridians(lon[::12],labels=[0,0,0,1],linewidth=0.5,fontsize=14)
m.drawparallels(lat[::4],labels=[1,0,0,0],linewidth=0.5,fontsize=14)

x, y = np.meshgrid(lon, lat)
X, Y = m(x, y)


C=m.contour(X, Y, strgrid,np.arange(-100e-7,100e-7,1e-8) )
plt.clabel(C,fmt='%g')
plt.show()
