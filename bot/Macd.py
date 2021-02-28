from Indicator import *
from Ema import Ema, EmaMacd
from utils import *

# Original source: https://github.com/jsmits/ta_python

class Macd(Indicator):
    """ Moving Average Convergence-Divergence (MACD) indicator class
            input:      data        = list or tuple of float or integer values
                        parameter   = tuple (x, y, z); where x is short term ema, y is long term ema, and z is ema of the macd"""
  
    def __init__(self, parameter, *args, **kwargs):
        Indicator.__init__(self, parameter, *args, **kwargs)
        self.input = []
        self.s_ema = Ema(parameter[0], self.key)
        self.l_ema = Ema(parameter[1], self.key)
        self.output = [] # macd
        self.ema_macd = EmaMacd(parameter[2])
        
    def calculate(self, candle):
        value = candle[self.key]
        self.input.append(float(value))
        self.s_ema.append(candle)
        self.l_ema.append(candle)
        
        outputvalue = None
        if len(self.input) >= self.parameter[1]:
            try:    
                outputvalue = self.s_ema[-1] - self.l_ema[-1]
            except:
                self.input = self.input[:-1]
                self.s_ema = self.s_ema[:-1]
                self.l_ema = self.l_ema[:-1]
                raise IndicatorError('error calculating macd value; reverting input data back to previous state')
        self.output.append(outputvalue)
        ema_macd_candle = None
        # make fake candle for ema_macd
        if outputvalue != None: 
            ema_macd_candle = {}
            ema_macd_candle['T'] = candle['T']
            ema_macd_candle['v'] = 0
            for elem in {'c', 'o', 'h', 'l' }:
                ema_macd_candle[elem] = outputvalue
        self.ema_macd.append(ema_macd_candle)
        
    def revertToPreviousState(self):
        # remove previous virtual candle
        Indicator.revertToPreviousState(self)
        self.input = self.input[:-1]
        self.output = self.output[:-1]
        self.s_ema.revertToPreviousState()
        self.l_ema.revertToPreviousState()
        self.ema_macd.revertToPreviousState()
    
    def validateParameter(self, parameter):
        if type(parameter) is not tuple:
            raise IndicatorError('invalid parameter for initializing Macd instance, should be an tuple; input: %s' % (self.parameter, ))
        if len(parameter) != 3:
            raise IndicatorError('invalid parameter for initializing Macd instance, should be an tuple with length 3 (e.g. 4,8,5); input: %s' % (self.parameter, ))
        if parameter[0] >= parameter[1]:
            raise IndicatorError('invalid parameter for initializing Macd instance, should be an tuple with length 3 (e.g. 4,8,5) and parameter 1 should be smaller than parameter 2; input: %s' % (self.parameter, ))
    
    # overrided functions
    def __str__(self):
        string = ''
        for i in range(len(self.input)):
            string+='%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (i+1, timestamp2str(self.times[i]), self.input[i], str(self.s_ema[i])[:7], str(self.l_ema[i])[:7], str(self.output[i])[:7], str(self.ema_macd[i]))
        return 'Macd(%s):\n%s' % (self.parameter, string)
    def __repr__(self):
        return 'Macd(%s)' % self.parameter
    def __len__(self):
        return len(self.output)
    def __getitem__(self, offset):
        return self.output[offset]
    def __getslice__(self, low, high):
        return self.output[low:high]

if __name__=='__main__':
    ind = Macd((3,6,3))

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

