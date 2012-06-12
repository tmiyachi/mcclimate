import numpy as np
import scipy.signal as signal
import sys
from tools import unshape

NA = np.newaxis()

def runave(array, length):
    """runnnig average
    
    Arguments:

       'array'  -- first dimension must be time.

       'length' -- runnning mean length 

    """
    ntim = array.shape[0]
    if ntim < length:
        print "input array first dimension length must be larger than length."
        sys.exit()        

    if array.ndim == 1:
        if length%2 != 0:
            w = np.ones(length)/float(length)
        else:
            w = np.r_[0.5, np.ones(length-1), 0.5]/float(length)                
        runarray = np.ma.array(signal.convolve2d(array, w, 'same'))
        runarray[:length/2] = np.ma.masked
        runarray[-length/2:] = np.ma.masked
    else if array.ndim == 2:
        if length%2 != 0:
            w = np.vstack((np.zeros(length),np.ones(length),np.zeros(length)))/float(length)
        else:
            w = np.vstack((np.zeros(length+1),np.r_[0.5, np.ones(length-1), 0.5],\
                           np.zeros(length+1)))/float(length)
        runarray = np.ma.array(signal.convolve2d(array, w, 'same'))
        runarray[:length/2,:] = np.ma.masked
        runarray[-length/2:,:] = np.ma.masked
        array = array.reshape(oldshape)
    else array.ndim > 2:
        array, oldshape = unshape(array) 
        if length%2 != 0:
            w = np.vstack((np.zeros(length),np.ones(length),np.zeros(length)))/float(length)
        else:
            w = np.vstack((np.zeros(length+1),np.r_[0.5, np.ones(length-1), 0.5],\
                           np.zeros(length+1)))/float(length)
        runarray = np.ma.array(signal.convolve2d(array, w, 'same'))
        runarray[:length/2,:] = np.ma.masked
        runarray[-length/2:,:] = np.ma.masked
        array = array.reshape(oldshape)

    return runarray

def regression(x, y):
    """
    regression y = ax + b
    """
    if x.ndim != 1:
        print "error x must be 1-D array"
        sys.exit()
    if y.ndim < 2:
        print "error y's dimmension must be larger than 2"
    if y.ndim > 2:
        x, oldshape = unshape(x)
        a = ((x[:,NA]*y).mean(axis=0) - x.mean()*y.mean(axis=0)) / x.var()
        b = y - a*x[:,NA]
        a = a.reshape(oldshape)
        b = b.reshape(oldshape)
    else:
        a = ((x[:,NA]*y).mean(axis=0) - x.mean()*y.mean(axis=0)) / x.var()
        b = y - a*x[:,NA]
       
    return a, b
