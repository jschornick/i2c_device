import smbus
import yaml
from i2c_register import I2CRegister

# TODO: make into properties if we can still call write_val()

class IntegerReg(I2CRegister):
    """ 8, 6, and 32 bit signed/unsigned ints """
    def __init__(self, bus, addr, conf, signed = True):
        I2CRegister.__init__(self, bus, addr, conf)
        if signed:
            self.bits = int(conf['type'][3:]) # type is intX or intXY
        else:
            self.bits = int(conf['type'][4:]) # type is uintX or uintXY
        self.bytes = self.bits/8
        self.signed = signed
        self.config['value_names'] = {}
        if 'values' in conf.keys():
            for value_num,val_name in conf['values'].items():
                self.config['value_names'][val_name] = value_num

    def read(self):
        value = 0
        # TODO: test block reads w/auto_inc for int32?
        if self.device.multi and (self.bytes == 2):
            value = self.device.read_word(self.address)
        else:
            for i in reversed(range(self.bytes)):
                value <<= 8
                value += self.read_byte(byte=i)
        # test highest bit
        if self.signed and value >> (self.bits-1):
            # two's compliment
            value -= (1<<self.bits)
        return value

    def write(self, value):
        if type(value) is str:
            value = self.config['value_names'][value]
        if self.signed:
            value += (1<<self.bits)  # two's copmliemnt
        for i in range(self.bytes):
            self.write_byte(byte=i, value=value & 0xff)
            value >>= 8

