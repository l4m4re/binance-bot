import datetime
from Indicator import *
from utils import *

# Original source: https://github.com/jsmits/ta_python

class Sma(Indicator):
    """ calculates Smooth Moving Average (SMA) indicator class """
   
    def __init__(self, N):
        Indicator.__init__(self, N)
        self.output = []

    def append(self, timestamp, value):

        Indicator.append(self,timestamp,value)
        
        outputvalue = None

        if len(self.input) >= self.N:
            try:    
                outputvalue = sum(self.input[(len(self.input)-self.N):len(self.input)]) / self.N
            except:
                self.input = self.input[:-1]
                raise IndicatorError('error calculating sma value; should never happen here')

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
            raise IndicatorError('invalid N for initializing Sma instance, should be an integer; input: %s' % (self.N, ))
        if N < 1:
            raise IndicatorError('invalid N for initializing Sma instance, should be an int > 0; input: %s' % (self.N, ))
    
    # override functions
    def __str__(self):
        string = ''
        for i in range(len(self.input)):
            string+='%s\t%s\t%s\t%s\n' % (i+1, timestamp2str(self.times[i]), self.input[i], str(self.output[i])[:9])
        return 'Sma(%s):\n%s' % (self.N, string)
    def __repr__(self):
        return 'Sma(%s)' % self.N
    def __len__(self):
        return len(self.output)
    def __getitem__(self, offset):
        return self.output[offset]
    def __getslice__(self, low, high):
        return self.output[low:high]
    


if __name__=='__main__':
    ind = Sma(6)

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
