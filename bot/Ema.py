from Indicator import *
from utils import *

# Original source: https://github.com/jsmits/ta_python

class Ema(Indicator):
    """ Exponential Moving Average (EMA) indicator class
            formula:    ((close - prev) * K) + prev """
    
    def __init__(self, parameter, *args, **kwargs):
        Indicator.__init__(self, parameter, *args, **kwargs)
        self.input = []
        self.output = []
        
    def calculate(self, candle):
        value = candle[self.key]
        self.input.append(float(value))
        outputvalue = None
        if len(self.input) == self.parameter: # first one is a sma
            try:
                outputvalue = sum(self.input[(len(self.input)-self.parameter):len(self.input)]) / self.parameter
            except:
                self.input = self.input[:-1]
                raise IndicatorError('error calculating first sma in ema; reverting input data back to previous state')
        if len(self.input) > self.parameter:
            try:    
                outputvalue = ((value - self.output[-1]) * (2.0 / (1+self.parameter))) + self.output[-1]
            except:
                self.input = self.input[:-1]
                raise IndicatorError('error calculating ema value; reverting input data back to previous state')
        self.output.append(outputvalue)

    def revertToPreviousState(self):
        # remove previous virtual candle
        Indicator.revertToPreviousState(self)
        self.input = self.input[:-1]
        self.output = self.output[:-1]
    
    def validateParameter(self, parameter):
        if type(parameter) is not int:
            raise IndicatorError('invalid parameter for initializing Ema instance, should be an integer; input: %s' % (self.parameter, ))
        if parameter < 1:
            raise IndicatorError('invalid parameter for initializing Ema instance, should be an int > 0; input: %s' % (self.parameter, ))
    
    # override functions
    def __str__(self):
        string = ''
        for i in range(len(self.input)):
            string+='%s\t%s\t%s\t%s\n' % (i+1, timestamp2str(self.times[i]), self.input[i], self.output[i])
        return 'Ema(%s):\n%s' % (self.parameter, string)
    def __repr__(self):
        return 'Ema(%s)' % self.parameter
    def __len__(self):
        return len(self.output)
    def __getitem__(self, offset):
        return self.output[offset]
    def __getslice__(self, low, high):
        return self.output[low:high]
    
class EmaMacd(Ema):
    """ Exponential Moving Average (EMA) of MACD indicator class
            formula:    ((close - prev) * K) + prev """
    def __init__(self, parameter, *args, **kwargs):
        Ema.__init__(self, parameter, *args, **kwargs)
        self.firstfilledindex = None
   
    def append(self, candle):
        if candle == None: 
            if not self.firstfilledindex:
                self.times.append(None)
                self.opens.append(None)
                self.highs.append(None)
                self.lows.append(None)
                self.closes.append(None)
                self.volumes.append(None)
                self.input.append(None)
                self.output.append(None)
                return
            else:
                raise IndicatorError('invalid input; None appended after real values in list')

        # need to know if it is a valid candle
        validateEmaMacdInput(candle, self.times)
        if self.firstfilledindex != 0 and not self.firstfilledindex:
            self.firstfilledindex = len(self.output)

        # check for virtual candle
        if len(self.times) > 0 and self.times[-1] == candle['T']:
            self.revertToPreviousState()

        self.calculate(candle)
        self.updateLists(candle)
        if self.times == None:
            self.firstfilledindex = None
    
    def revertToPreviousState(self):
        # remove previous virtual candle
        Indicator.revertToPreviousState(self)
        self.input = self.input[:-1]
        self.output = self.output[:-1]
        
    def calculate(self, candle):
        value = candle[self.key]
        self.input.append(float(value))
        outputvalue = None
        if len(self.input) == self.firstfilledindex + self.parameter: # first one is a sma
            try:
                outputvalue = sum(self.input[(len(self.input)-self.parameter):len(self.input)]) / self.parameter
            except:
                self.input = self.input[:-1]
                raise IndicatorError('error calculating first sma in ema_macd; reverting input data back to previous state')
        if len(self.input) > self.firstfilledindex + self.parameter:
            try:    
                outputvalue = ((value - self.output[-1]) * (2.0 / (1+self.parameter))) + self.output[-1]
            except:
                self.input = self.input[:-1]
                raise IndicatorError('error calculating ema_macd value; reverting input data back to previous state')
        self.output.append(outputvalue)
    
    # override functions
    def __str__(self):
        string = ''
        for i in range(len(self.input)):
            string+='%s\t%s\t%s\t%s\n' % (i+1, timestamp2str(self.times[i]), self.input[i], self.output[i])
        return 'EmaMacd(%s):\n%s' % (self.parameter, string)
    def __repr__(self):
        return 'EmaMacd(%s)' % self.parameter
    def __len__(self):
        return len(self.output)
    def __getitem__(self, offset):
        return self.output[offset]
    def __getslice__(self, low, high):
        return self.output[low:high]
    
def validateEmaMacdInput(candle, times):
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

    if len(times) > 0 and times[-1] != None and candle['T'] < times[-1]: 
        raise InvalidDateTimeError('invalid input: dict element ["T"] (datetime) should be equal or greater than previous: %s; input: %s' % (self.times[-1], candle['T']))  


if __name__=='__main__':
    ind = Ema(6)

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
    for i in input:
        ind.append(i)
    print(ind)
    
    ind = EmaMacd(6)
    input = [None]*4 + input
    for i in input:
        ind.append(i)
    print(ind)
    
    
