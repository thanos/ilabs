"""

Utility code 

(c) syntazo 1996- 2016

syntazo opensource

coded by: thanos vassilakis

$RCSfile: __init__.py,v $
$Date: 2004/07/16 17:31:52 $
$Revision: 1.2 $

"""

import os
from optparse import OptionParser


class List(list):
    deferChange = False
    onChange = None

    def __init__(self, *args):
        list.__init__(self, *args)
        if self.onChange: self.onChange(self.__init__, *args)

    def __setitem__(self, i, item):
        list.__setitem__(self, i, item)
        if self.onChange: self.onChange(self.__setitem__, i, item)

    def __delitem__(self, i):
        list.__delitem__(self, i, item)
        if self.onChange: self.onChange(self.__delitem__, i)

    def __setslice__(self, i, j, other):
        list.__setslice__(self, i, j, other)
        if self.onChange: self.onChange(self.__setslice__, i, j, other)

    def __delslice__(self, i, j):
        list.__setslice__(self, i, j, other)
        if self.onChange: self.onChange(self.__delslice__, i, j)

    def __mul__(self, n):
        result = list.__mul__(self, n)
        if self.onChange: self.onChange(self.__mul__, n)
        return result

    __rmul__ = __mul__

    def __imul__(self, n):
        list.__imul__(self, n)
        if self.onChange: self.onChange(self.__imul__, n)
        return self

    def append(self, value):
        list.append(self, value)
        if self.onChange: self.onChange(self.append, value)


class ArgsParser(OptionParser):
    USAGE = "usage: %prog [options] arg1 arg2"

    def __init__(self):
        OptionParser.__init__(self, usage=self.USAGE)
        self.config()
        self.process()

    def config(self):
        """
        do something like this
        self.add_option("-c", "--config",  dest="cfgfile", help="your config file", metavar="CONFIG_FILE")
        """

    def process(self):
        self.opts, self.args = self.parse_args()
        self.validate()

    def validate(self):
        """
        add something like this
        self.readable_required('-c')
        """

    def readable_required(self, opt):
        options, value = self.check_required(opt)
        if not os.access(value, os.F_OK | os.R_OK):
            self.error('cannot read from file: %s' % value)
        return value

    def writable_required(self, opt):
        options, value = self.check_required(opt)
        if not os.access(value, os.F_OK):
            try:
                path = os.path.split(value)[0]
                if path:
                    os.makedirs(path)
            except Exception, e:
                self.error('failed to create path: %s' % value)
        elif not os.access(value, os.W_OK):
            self.error('canot write to output path: %s' % value)
        return value

    def check(self, opt):
        option = self.get_option(opt)
        value = getattr(self.values, option.dest)
        if value is not None:
            return option, getattr(self.values, option.dest)

    def check_required(self, opt):
        option = self.get_option(opt)
        value = getattr(self.values, option.dest)
        if value is not None:
            return option, getattr(self.values, option.dest)
        self.error("%s option not supplied" % option)


if __name__ == '__main__':
    class MyList(List):
        def onChange(self, *args):
            print()'onChange', args)


    l = MyList((1, 2, 3, 4, 5))
    l.append(10)
    l[4] = '4'
    l[4:5] = '4'

    print(l)
