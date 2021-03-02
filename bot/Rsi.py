from Indicator import *
from Ema import Ema
from utils import *

# Based on: https://github.com/jsmits/ta_python

class Rsi(Indicator):
    """ Relative Strength Index (RSI) indicator class
            input:      data        = list or tuple of float or integer values
                        N           = ema length """
  
    def __init__(self, N, K=None):
        Indicator.__init__(self, N)
        self.output   = [] # rsi
        self.u_ema    = Ema(N,K)
        self.d_ema    = Ema(N,K)
        
    def append(self, timestamp, value):
        Indicator.append(self,timestamp,value)

        prev_close = 0.0

        if len(self.input) > 1:
            prev_close = self.input[-2] # value already added to input by parent

            if prev_close < value:
                self.u_ema.append(timestamp, value - prev_close)
                self.d_ema.append(timestamp, 0.0)
            else:
                self.u_ema.append(timestamp, 0.0)
                self.d_ema.append(timestamp, prev_close - value)
        else:
            self.u_ema.append(timestamp, 0.0)
            self.d_ema.append(timestamp, 0.0)

        outputvalue = None

        if len(self.input) >= self.N:
            try:   
                rs = self.u_ema[-1] / self.d_ema[-1] 

                #print("current rs:", rs)

                outputvalue = 100.0 - (100.0/(1.0+rs))
            except:
                self.input = self.input[:-1]
                self.u_ema = self.d_ema[:-1]
                self.d_ema = self.d_ema[:-1]
                raise IndicatorError('error calculating rsi value; reverting input data back to previous state')

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
        self.u_ema.popHead()
        self.d_ema.popHead()

    def popTail(self):
        # remove previous virtual candle
        Indicator.popTail(self)
        self.output = self.output[:-1]
        self.u_ema.popTail()
        self.d_ema.popTail()

    
    def validateN(self, N):
        if type(N) is not int:
            raise IndicatorError('invalid N for initializing Rsi instance, should be an int; input: %s' % (self.N, ))
    
    # overrided functions
    def __str__(self):
        string = ''
        for i in range(len(self.input)):
            string += '%s\t%s\t%s\t%s\t%s\t%s\n' % (i+1, timestamp2str(self.times[i]), self.input[i],
                        str(self.u_ema[i])[:7], str(self.d_ema[i])[:7], str(self.output[i])[:7])
        return 'Rsi(%s):\n%s' % (self.N, string)
    def __repr__(self):
        return 'Rsi(%s)' % self.N
    def __len__(self):
        return len(self.output)
    def __getitem__(self, offset):
        return self.output[offset]
    def __getslice__(self, low, high):
        return self.output[low:high]

if __name__=='__main__':
    ind = Rsi(6)

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
        ind.appendCandle(i)
    print(ind)


    ind = Rsi(6,0.1)
    for i in input:
        ind.appendCandle(i)
    print(ind)
   


