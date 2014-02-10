import smbus
import yaml
from i2c_register import I2CRegister

# TODO: add null-terminated option
class StringReg(I2CRegister):

    def __init__(self, bus, addr, conf):
        I2CRegister.__init__(self, bus, addr, conf)
        self.length = self.config['length']

    def read(self):
        value = ""
        for i in range(self.length):
            value += chr(self.read_byte(byte=i))
        return value

    def write(self, value):
        for i in range(self.length):
            self.write_byte(ord(value[i]),byte=i)

