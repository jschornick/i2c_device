import smbus
import yaml

""" Abstract I2C register class """

class I2CRegister(object):

    def __init__(self, device, address, config):
        self.address = address  # register address
        self.device = device
        self.read_byte = lambda byte=0: device.read_byte(self.address+byte)
        self.write_byte = lambda value,byte=0: device.write_byte(self.address+byte, value)
        self.config = config
        if 'name' in config.keys():
            self.name = config['name']
        else:
            self.name = hex(address)

    def read(self):
        print "WARNING: not implemented"
        return 0x00

    def write(self):
        print "WARNING: not implemented"
    
    def __str__(self):
        return "I2C register {:#04x} '{}'".format(
                self.address,self.config['name'])

