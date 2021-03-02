from Indicator import *
from utils import *

# Original source: https://github.com/jsmits/ta_python

# https://sciencing.com/calculate-exponential-moving-averages-8221813.html
# 
# The exponential moving average formula is:
# 
# EMA = (closing price − previous day's EMA) × smoothing constant + previous day's EMA
# 
# where the smoothing constant is:
# 
# 2 ÷ (number of time periods + 1)
# 


class Ema(Indicator):
    """ Exponential Moving Average (EMA) indicator class
            formula:    ((close - prev) * K) + prev """
    
    def __init__(self, N, K=None):
        Indicator.__init__(self, N)
        self.output = []
        if K == None:
           self.K = (2.0 / (1+self.N)) 
        else:
           self.K = K

        # dprint("Self.N: " + str(self.N) + " Self.K: " + str(self.K))

    def append(self,timestamp,value):
        Indicator.append(self,timestamp,value)

        outputvalue = None

        if len(self.input) == self.N: # first one is a sma
            try:
                outputvalue = sum(self.input[(len(self.input)-self.N):len(self.input)]) / self.N
            except:
                Indicator.popTail(self)
                raise IndicatorError('error calculating first sma in ema; reverting input data back to previous state')
        if len(self.input) > self.N:
            try:    
                outputvalue = ((self.input[-1] - self.output[-1]) * self.K) + self.output[-1]
            except:
                Indicator.popTail(self)
                raise IndicatorError('error calculating ema value; reverting input data back to previous state')

        self.output.append(outputvalue)

        return self.lastOutput()

    def lastOutput(self): 
        if len(self.output) > 0:
            return self.output[-1]
        return None


    def popHead(self):
        # remove previous virtual candle
        Indicator.popHead(self)
        self.output = self.output[1:]

    def popTail(self):
        # remove previous virtual candle
        Indicator.popTail(self)
        self.output = self.output[:-1]


    
    def validateN(self, N):
        if type(N) is not int:
            raise IndicatorError('invalid N for initializing Ema instance, should be an integer; input: %s' % (self.N, ))
        if N < 1:
            raise IndicatorError('invalid N for initializing Ema instance, should be an int > 0; input: %s' % (self.N, ))
    
    # override functions
    def __str__(self):
        string = ''
        for i in range(len(self.input)):
            string+='%s\t%s\t%s\t%s\n' % (i+1, timestamp2str(self.times[i]), self.input[i], self.output[i])
        return 'Ema(%s):\n%s' % (self.N, string)
    def __repr__(self):
        return 'Ema(%s)' % self.N
    def __len__(self):
        return len(self.output)
    def __getitem__(self, offset):
        return self.output[offset]
    def __getslice__(self, low, high):
        return self.output[low:high]
    
class EmaMacd(Ema):
    """ Exponential Moving Average (EMA) of MACD indicator class
            formula:    ((close - prev) * K) + prev """
    def __init__(self, N, K=None):
        Ema.__init__(self, N, K)
        self.firstfilledindex = None

   
    def append(self, timestamp, value):

        if timestamp == None or value == None: 
            if not self.firstfilledindex:
                self.times.append(None)
                self.input.append(None)
                self.output.append(None)
                return
            else:
                raise IndicatorError('invalid input; None appended after real values in list')

        Indicator.append(self,timestamp,value)

        if self.firstfilledindex != 0 and not self.firstfilledindex:
            self.firstfilledindex = len(self.output)

        outputvalue = None

        if len(self.input) == self.firstfilledindex + self.N: # first one is a sma
            try:
                outputvalue = sum(self.input[(len(self.input)-self.N):len(self.input)]) / self.N
            except:
                Indicator.popTail(self)
                raise IndicatorError('error calculating first sma in ema_macd; reverting input data back to previous state')
        if len(self.input) > self.firstfilledindex + self.N:
            try:    
                outputvalue = ((self.input[-1] - self.output[-1]) * self.K) + self.output[-1]
            except:
                Indicator.popTail(self)
                raise IndicatorError('error calculating ema_macd value; reverting input data back to previous state')

        self.output.append(outputvalue)

        if self.times == None:
            self.firstfilledindex = None

        return self.lastOutput()


    def lastOutput(self):
        if len(self.output) > 0:
          return self.output[-1]
        return None


    def popHead(self):
        Indicator.popHead(self)
        self.input = self.input[1:]
        self.output = self.output[1:]

    def popTail(self):
        # remove previous virtual candle
        Indicator.popTail(self)
        self.output = self.output[:-1]


    # override functions
    def __str__(self):
        string = ''
        for i in range(len(self.input)):
            ts = None 
            if self.times[i] != None:
                ts = timestamp2str(self.times[i])

            string+='%s\t%s\t%s\t%s\n' % (i+1, ts, self.input[i], self.output[i])
        return 'EmaMacd(%s):\n%s' % (self.N, string)

    def __repr__(self):
        return 'EmaMacd(%s)' % self.N
    def __len__(self):
        return len(self.output)
    def __getitem__(self, offset):
        return self.output[offset]
    def __getslice__(self, low, high):
        return self.output[low:high]
'''        
    def validatedInput(self, candle):
        print("validateInput EmaMacd called.")

        if type(candle) is not dict:
            raise NotTupleError('invalid input: should be a dict with (c, T, o, h, l, v); input: %s' % (candle, ))
        if len(candle) < 6:
            raise InvalidCandleStickError('invalid input: dict length should be 6 or more; input: %s' % (candle, ))
        if not type(candle['T']) is int:
            raise InvalidDateTimeError('invalid input: dict element ["T"] should be an int; input: %s' % (candle['T'], ))
        for i in {'c', 'o', 'h', 'l', 'v' }:
            if type(candle[i]) is not int and type(candle[i]) is not float:
                raise InvalidCandleStickError('invalid input: dict element [%s] is not int or float; input: %s' % (i, candle[i]))
        if candle['h'] < candle['l']:
            raise InvalidCandleStickError('invalid input: high: %s is lower than low: %s' % (candle['h'], candle['l']))
        if candle['o'] > candle['h'] or candle['o'] < candle['l']:
            raise InvalidCandleStickError('invalid input: open (%s) is outside high (%s) - low (%s) range' % (candle['o'], candle['h'], candle['l']))
        if candle['c'] > candle['h'] or candle['c'] < candle['l']:
            raise InvalidCandleStickError('invalid input: close (%s) is outside high (%s) - low (%s) range' % (candle['c'], candle['h'], candle['l']))

        if len(self.times) > 0 and self.times[-1] != None and candle['T'] < self.times[-1]: 
            raise InvalidDateTimeError(
                'invalid input: dict element ["T"] (datetime) should be equal or greater than previous: %s; input: %s' 
                % (self.times[-1], candle['T']))  

'''        


if __name__=='__main__':

    input = [
            {"c": 7186.68000000, "T": 1577836859999, "o": 7195.24000000, "h": 7196.25000000, "l": 7183.14000000, "v": 51.64281200},
            {"c": 7184.03000000, "T": 1577836919999, "o": 7187.67000000, "h": 7188.06000000, "l": 7182.20000000, "v": 7.24814800},
            {"c": 7182.43000000, "T": 1577836979999, "o": 7184.41000000, "h": 7184.71000000, "l": 7180.26000000, "v": 11.68167700},
            {"c": 7185.94000000, "T": 1577837039999, "o": 7183.83000000, "h": 7188.94000000, "l": 7182.49000000, "v": 10.02539100},
            {"c": 7179.78000000, "T": 1577837099999, "o": 7185.54000000, "h": 7185.54000000, "l": 7178.64000000, "v": 14.91110500},
            {"c": 7179.99000000, "T": 1577837159999, "o": 7179.76000000, "h": 7182.51000000, "l": 7178.20000000, "v": 12.46324300},
            {"c": 7182.00000000, "T": 1577837219999, "o": 7180.00000000, "h": 7182.00000000, "l": 7179.99000000, "v": 3.57377400},
            {"c": 7183.66000000, "T": 1577837279999, "o": 7181.70000000, "h": 7183.77000000, "l": 7180.91000000, "v": 14.47078200},
            {"c": 7187.68000000, "T": 1577837339999, "o": 7183.90000000, "h": 7187.74000000, "l": 7183.45000000, "v": 12.84244300},
            {"c": 7191.07000000, "T": 1577837399999, "o": 7187.68000000, "h": 7191.77000000, "l": 7186.02000000, "v": 16.01498300},
            {"c": 7187.36000000, "T": 1577837459999, "o": 7193.15000000, "h": 7193.53000000, "l": 7186.25000000, "v": 12.60237000},
            {"c": 7188.71000000, "T": 1577837519999, "o": 7187.36000000, "h": 7191.08000000, "l": 7186.82000000, "v": 10.26352500},
            {"c": 7187.02000000, "T": 1577837579999, "o": 7189.52000000, "h": 7189.52000000, "l": 7187.00000000, "v": 2.86041300}, 
            {"c": 7182.08000000, "T": 1577837639999, "o": 7187.02000000, "h": 7187.02000000, "l": 7181.61000000, "v": 13.23039300}, 
            {"c": 7180.97000000, "T": 1577837699999, "o": 7181.60000000, "h": 7182.10000000, "l": 7180.24000000, "v": 9.11180900}, 
                      ]
    ind = Ema(6)
    for i in input:
        ind.appendCandle(i)
    print(ind)


    ind = Ema(2,0.2857142857142857)
    for i in input:
        ind.appendCandle(i)
    print(ind)
    
    ind = EmaMacd(6)
    ind.append(1577837699999, None) 
    for i in input:
        ind.append(i['T'],i['c'])
    print(ind)
    
    ind = EmaMacd(6)
    ind.append(None, None) 
    for i in input:
        ind.append(i['T'],i['c'])
    print(ind)



    ind = EmaMacd(6)
    input = [None]*4 + input
    for i in input:
        ind.appendCandle(i)
    print(ind)
    
    
