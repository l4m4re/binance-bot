import utils

# Original source: https://github.com/jsmits/ta_python

# define exceptions
class IndicatorError(Exception): pass
class InvalidCandleStickError(IndicatorError): pass
class NotTupleError(InvalidCandleStickError): pass
class NotFloatError(InvalidCandleStickError): pass
class InvalidDateTimeError(InvalidCandleStickError): pass
class IndicatorSignalError(IndicatorError): pass

class Indicator:
    def __init__(self, N):
        self.N     = N
        self.validateN(self.N)
        self.key   = 'c' # close
        self.times =[]
        self.input =[]

        
    def appendCandle(self, candle):

        if candle == None:
            return self.append(None, None)

        # check if valid input
        try:
            self.validateInput(candle)
        except InvalidDateTimeError as e:
           print("Validation failed, ignoring: " + str(e)) 
           return None

        return self.append(candle['T'],float(candle[self.key])) 


    def append(self, timestamp, value):
        # check for virtual candle
        if len(self.times) > 0 and self.times[-1] == timestamp:
            self.popTail()

        n = self.N
        if type(self.N) is tuple:  # Macd instance
            n = self.N[1]

        # No need to grow big arrays
        if len(self.times) > max(20, n):
            self.popHead()

        self.times.append(timestamp)
        self.input.append(value)

        return self.lastOutput()

    def lastOutput(self):
        pass

    def popHead(self):
        self.times = self.times[1:]
        self.input = self.input[1:]

    def popTail(self):
        self.times = self.times[:-1]
        self.input = self.input[:-1]

    def calculate(self, candle):
        pass
    
    def validateN(self, N):
        pass
    
    def sanityCheck(self, candle):
        pass
    
    def validateInput(self, candle):

        if type(candle) is not dict:
            raise NotTupleError('invalid input: should be a dict with (c, T, o, h, l, v); input: %s' % (candle ))
        if len(candle) < 6:
            raise InvalidCandleStickError('invalid input: dict length should be 6 or more; input: %s' % (candle ))
        if not type(candle['T']) is int:
            raise InvalidDateTimeError('invalid input: dict element ["T"] should be an int; input: %s' % (candle[0], ))
        for i in {'c', 'o', 'h', 'l', 'v' }:
            if type(candle[i]) is not int and type(candle[i]) is not float:
                raise InvalidCandleStickError('invalid input: dict element [%s] is not int or float; input: %s' % (i, candle[i]))
        for i in {'c', 'o', 'h', 'l' }:
            if candle[i] <= 0:
                raise InvalidCandleStickError('invalid input: dict element [%s] is equal or less than 0; input: %s' % (i, candle[i]))
        if candle['h'] < candle['l']:
            raise InvalidCandleStickError('invalid input: high: %s is lower than low: %s' % (candle['h'], candle['l']))
        if candle['o'] > candle['h'] or candle['o'] < candle['l']:
            raise InvalidCandleStickError('invalid input: open (%s) is outside high (%s) - low (%s) range' % (candle['o'], candle['h'], candle['l']))
        if candle['c'] > candle['h'] or candle['c'] < candle['l']:
            raise InvalidCandleStickError('invalid input: close (%s) is outside high (%s) - low (%s) range' % (candle['c'], candle['h'], candle['l']))

        if len(self.times) > 0 and self.times[-1] != None and candle['T'] < self.times[-1]: 
            raise InvalidDateTimeError(
                'invalid input: dict element ["T"] (datetime) should be equal or greater than previous: %s; input: %s' %
                 (self.times[-1], candle['T']))  

