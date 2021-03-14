import json, pprint, talib, numpy
import config
import sys, time, os
import numpy as np
from trader import *
from broker import *
from utils import *
import copy
import math

#TRADE_SYMBOL    = "THETAUSDT"
TRADE_SYMBOL    = "BTCUSDT"
#TICKER_FILE     = "../data/BTCUSDT_2020_1minutes.txt"
#TICKER_FILE     = "../data/BTCUSDT_2021_1minutes_2.txt"
TICKER_FILE     = "../data/BTCUSDT_2018-2020.txt"
TRADE_QUANTITY  = 10

trader = None
broker = None


def par2np(par):
    return np.array([
        math.log(par['len_fac'])/math.log(100),
        math.log(par['sma_len_fac'])/math.log(10),
        math.log(par['rsi_len_fac'])/math.log(10),
        math.log(par['ema_len_fac'])/math.log(10),
        math.log(par['macd_len_fac'])/math.log(10),
        par['fast_multiplier'],
        par['slow_multiplier'],
        par['macd_multiplier'],
        par['sma_fac']/10,
        par['rsi_fac']/10,
        par['ema_fac']/10,
        par['mac_fac']/10,
        par['offset']/10,
        par['am_fac']/10,
        par['am_offset']/10,
    ]) 

def np2par(np):
    par = {}

    par['len_fac']         = math.pow(100,np[0])
    par['sma_len_fac']     = math.pow(10,np[1])
    par['rsi_len_fac']     = math.pow(10,np[2])
    par['ema_len_fac']     = math.pow(10,np[3])
    par['macd_len_fac']    = math.pow(10,np[4])
    par['fast_multiplier'] = np[5]
    par['slow_multiplier'] = np[6]
    par['macd_multiplier'] = np[7]
    par['sma_fac']         = np[8]*10
    par['rsi_fac']         = np[9]*10
    par['ema_fac']         = np[10]*10
    par['mac_fac']         = np[11]*10
    par['offset']          = np[12]*10
    par['am_fac']          = np[13]*10
    par['am_offset']       = np[14]*10

    return par



'''
    Pure Python/Numpy implementation of the Nelder-Mead algorithm.
    Reference: https://en.wikipedia.org/wiki/Nelder%E2%80%93Mead_method
'''
# source: https://github.com/fchollet/nelder-mead

# Changed Changed expansion & contraction to be consistent with wiki
# along: https://github.com/yw5aj/nelder-mead
# Changed default for rho from -0.5 to 0.5 to be consistent with wiki

def nelder_mead(f, x_start,
                step=0.1, no_improve_thr=10e-14,
                no_improv_break=60, max_iter=0,
                alpha=1., gamma=2., rho=0.5, sigma=0.5):
    '''
        @param f (function): function to optimize, must return a scalar score
            and operate over a numpy array of the same dimensions as x_start
        @param x_start (numpy array): initial position
        @param step (float): look-around radius in initial step
        @no_improv_thr,  no_improv_break (float, int): break after no_improv_break iterations with
            an improvement lower than no_improv_thr
        @max_iter (int): always break after this number of iterations.
            Set it to 0 to loop indefinitely.
        @alpha, gamma, rho, sigma (floats): parameters of the algorithm
            (see Wikipedia page for reference)

        return: tuple (best parameter array, best score)
    '''


    print("Nelder-mead parameters:", alpha, gamma, rho, sigma )

    # init
    dim = len(x_start)
    prev_best = f(x_start)
    no_improv = 0
    res = [[x_start, prev_best]]

    for i in range(dim):
        x = copy.copy(x_start)
        x[i] = x[i] + step
        score = f(x)
        res.append([x, score])

    # simplex iter
    iters = 0
    while 1:
        # order
        res.sort(key=lambda x: x[1])
        best = res[0][1]

        # break after max_iter
        if max_iter and iters >= max_iter:
            return res[0]
        iters += 1

        # break after no_improv_break iterations with no improvement
        dprint('...best so far: ' + str(best))
        dpprint(res[0])

        if best < prev_best - no_improve_thr:
            no_improv = 0
            prev_best = best
        else:
            no_improv += 1

        if no_improv >= no_improv_break:
            return res[0]

        # centroid
        x0 = [0.] * dim
        for tup in res[:-1]:
            for i, c in enumerate(tup[0]):
                x0[i] += c / (len(res)-1)

        # reflection
        xr = x0 + alpha*(x0 - res[-1][0])
        rscore = f(xr)
        if res[0][1] <= rscore < res[-2][1]:
            del res[-1]
            res.append([xr, rscore])
            continue

        # expansion
        if rscore < res[0][1]:
            #xe = x0 + gamma*(x0 - res[-1][0])
            xe = x0 + gamma*(xr - x0)
            escore = f(xe)
            if escore < rscore:
                del res[-1]
                res.append([xe, escore])
                continue
            else:
                del res[-1]
                res.append([xr, rscore])
                continue

        # contraction
        #xc = x0 + rho*(x0 - res[-1][0])
        xc = x0 + rho*(res[-1][0] - x0)
        cscore = f(xc)
        if cscore < res[-1][1]:
            del res[-1]
            res.append([xc, cscore])
            continue

        # reduction
        x1 = res[0][0]
        nres = []
        for tup in res:
            redx = x1 + sigma*(tup[0] - x1)
            score = f(redx)
            nres.append([redx, score])
        res = nres



results = []

count = 0
    
def f(x):
    global results
    global count

    parameters = np2par(x)
    '''
    if parameters['ema_K']     > 0.99   or parameters['ema_K']     <= 0: return 1111.1
    #if parameters['rsi_K']     > 0.99   or parameters['rsi_K']     <= 0: return 1111.1
    if parameters['emamacd_K'] > 0.99   or parameters['emamacd_K'] <= 0: return 2222.2
    if parameters['fast_K']    > 0.99   or parameters['fast_K']    <= 0: return 3333.3
    if parameters['macd_K']    > 0.99   or parameters['macd_K']    <= 0: return 4444.4
    if parameters['slow_K']    > 0.99   or parameters['slow_K']    <= 0: return 5555.5
    if parameters['sma_length']> 100000 or parameters['sma_length']<= 5: return 6666.6
    '''

    '''
    if parameters['len_fac']          <= 0: return 1111.1
    if parameters['sma_len_fac']      <= 0: return 1111.1
    if parameters['ema_len_fac']      <= 0: return 1111.1
    '''
    if parameters['fast_multiplier']  <= 0: return 1111.1
    if parameters['slow_multiplier']  <= 0: return 1111.1
    if parameters['macd_multiplier']  <= 0: return 1111.1
 
    # ToDo: Check actual length, b/c these can become equal because of
    # rounding
    if parameters['slow_multiplier']  <= parameters['fast_multiplier']: return 1111.1


    for (par,r) in results:
        if par == parameters:
            dprint( "Returned result from cache: " + str(r) )
            return r

    count = count + 1


    #dprint("Running trader with parameters:")
    #dpprint(parameters)

    broker = Broker()
    trader = Trader(broker,parameters)
    
    datafile = open(TICKER_FILE,"r")
    for line in datafile:

        candle = {}
        inpcandle = json.loads(line)

        candle['T'] = int(inpcandle['T'])
        for elem in {'c', 'o', 'h', 'l', 'v' }:
            candle[elem] = float(inpcandle[elem])

        trader.append( candle )

    #result = -1 * broker.avgprofit * broker.ntrades
    profit = 100*(broker.cash + broker.cur_close*broker.cryptoamount - broker.begincash)/broker.begincash
    result = -1*profit

    dprint("Run nr. : " + str(count))
    dprint("Profit  : " + str(round(profit,2)) + "% in " + str(broker.ntrades) + " trades" )
    dprint("Result  : " + str(result))

    results.append((parameters, result))

    return result
    


if __name__ == '__main__':

    parameters = { 
                    'am_fac': 1.0126044146312323,
                    'am_offset': -1.390291787077809,
                    'ema_fac': 1.0423760605896413,
                    'ema_len_fac': 31.19076727111527,
                    'fast_multiplier': 1.1665571476188767,
                    'len_fac': 56.47278220507966,
                    'mac_fac': 1.0815747464202425,
                    'macd_len_fac': 28.746186886243123,
                    'macd_multiplier': 0.46439394433353964,
                    'offset': 0.10882543923569951,
                    'rsi_fac': -0.0185862377434674,
                    'rsi_len_fac': 32.07658980577076,
                    'slow_multiplier': 1.4281917805361604,
                    'sma_fac': 1.0243458576551303,
                    'sma_len_fac': 274.42349384873654
                 }

    '''
    parameters = { 'len_fac'         : 60,
                   'sma_len_fac'     : 200, 
                   'ema_len_fac'     : 30, 
                   'rsi_len_fac'     : 30, 
                   'macd_len_fac'    : 30, 
                   'fast_multiplier' : 1.15,
                   'slow_multiplier' : 1.4,
                   'macd_multiplier' : 0.45,
                   'sma_fac'         : 1.0,
                   'rsi_fac'         : 0.01,
                   'ema_fac'         : 1.0, 
                   'mac_fac'         : 1.0,
                   'offset'          : 0.0,
                   'oversold'        : -0.5,
                   'overbought'      : 0.5 }
    '''

    #parameters = {
    #                #'rsi_K': 0.00016665277893508876,
    #                'ema_K': 0.0016652789342214821,
    #                'emamacd_K': 0.0036968576709796672,
    #                'fast_K': 0.001448225923244026,
    #                'macd_K': 0.0036968576709796672,
    #                'slow_K': 0.0012812299807815502,
    #                'sma_length': 12000
    #             }


    #parameters = {   'ema_K': 0.06038605001415557,
    #                 'ema_fac': 1.0192756888777887,
    #                 'emamacd_K': 0.00639715577386981,
    #                 'fast_K': 0.0003444088572024939,
    #                 'mac_fac': 1.029750783392093,
    #                 'macd_K': 0.01078497549921677,
    #                 'offset': 0.12452596641099553,
    #                 'slow_K': 0.00015492283801938668,
    #                 'sma_fac': 1.0114543836194274,
    #                 'sma_length': 127
    # Average profit:17.87% in 4 trades on BTCUSDT_2021_1minutes_2.txt


    '''
    INFO:root:2021-03-03 01:18:30.410768: Run nr.              : 212
    INFO:root:2021-03-03 01:18:30.412376: Average        profit: 1.1% in 208 trades
    INFO:root:2021-03-03 01:18:30.412776: Multiplicative result: 2.89x in 208 trades
    INFO:root:2021-03-03 01:18:30.413280: Result               : -2.8876642094057097
    INFO:root:2021-03-03 01:18:31.329094: Trader started with  parameters:
    INFO:root:2021-03-03 01:18:31.329476: {'ema_K': 0.0023472325013832174,
     'emamacd_K': 0.002662756676950587,
     'fast_K': 0.0014130751290235676,
     'macd_K': 0.004308626575991549,
     'slow_K': 0.0008633103738817601,
     'sma_length': 12056}
    '''

    ''' 
    dprint("Starting loop:")

    len_fac = 22
    for loop in range(1,10):
        parameters['len_fac'] = len_fac
        len_fac = len_fac * 2
        nppars = par2np(parameters)
        dpprint(parameters)
        print( f(nppars) )
    '''
        

    dprint("Starting optimizer with parameters:")
    dpprint(parameters)

    nppars = par2np(parameters)
    #pprint.pprint(nppars)

    #pars = np2par(nppars)
    #pprint.pprint(pars)

    # Determine Nelder Mead parameters according to https://www.webpages.uidaho.edu/~fuchang/res/ANMS.pdf
    n = len(parameters)
    _alpha = 1.0
    _gamma = 1 + 2/n
    _rho   = 0.75-1/(2*n)
    _sigma = 1 - 1/n


    print(nelder_mead(f, nppars, alpha=_alpha, gamma=_gamma, rho=_rho, sigma=_sigma))
   

