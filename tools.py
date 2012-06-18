import numpy
import sys
import scipy.signal
from dateutil import parser
from datetime import timedelta

def unshape(arraynd):
    """reshape multidimensional array to 2D array. 

    Arguments:

      'arraynd'  -- N-dimensional NumPy array (N>=2)

    Returns: a tuple (array2d, oldshape)

      'array2d'  -- 2-dimensional array.

      'oldshape' -- input N-dimensional array's shape

    """
    if arraynd.ndim < 2:
        print "input N-dimensional array must be N>2."
        sys.exit()

    oldshape = arraynd.shape
    array2d = arraynd.reshape(oldshape[0],-1)
    
    return array2d, oldshape

class Timemask():
    #mask array for sequential time series manipuration
    def __init__(self, start, end):
        '''
        time sampling is days only!!
        
        Arguments:

            start -- start date string  ex. 1979-6-3

            end   -- end date string
        '''
        startdate = parser.parse(start)
        enddate = parser.parse(end)
        deltadate = timedelta(days=1)
        tnum = (enddate-startdate).days+1

        self.timeint = numpy.array([int((startdate + deltadate*i).strftime('%Y%m%j')) for i in range(tnum)])
        self.year = self.timeint/100000
        self.month = self.timeint%100000/1000
        self.days = self.timeint%1000
