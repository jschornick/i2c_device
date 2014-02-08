import smbus
import yaml

class I2CDevice(object):

    def __init__(self, bus, address, config=None):
        self.busnum = bus
        try:
            self.bus = smbus.SMBus(bus)
        except IOError as e:
            self.bus = None
            print "Could not open I2C bus {}: {}".format(bus,e)
        self.address = address
        if config:
            with file(config) as f:
                self.config = yaml.load(f)
            self.process_config(self.config)

    def read_byte(self, register):
        #print "Reading addr:", self.address, ", reg:", register
        return self.bus.read_byte_data(self.address, register)

    def write_byte(self, register, value):
        return self.bus.write_byte_data(self.address, register, value)

    def process_config(self, config):
        self.name = config['name']
        self.registers = {}
        for reg_addr,reg_conf in config['registers'].items():
            #self.registers[reg['name']] = I2CRegister(self.bus,self.address,reg)
            #self.registers[reg_conf['name']] = I2CRegister(
            #        self.read_byte,self.write_byte,reg_addr,reg_conf)
            name = reg_conf['name']
            try:
                reg_type = reg_conf['type']
            except KeyError:
                reg_type = None
            if reg_type in ['int8', 'int16', 'int32']:
                self.registers[name] = IntReg(self,reg_addr,reg_conf)
            elif reg_type == 'bitfield':
                self.registers[name] = BitfieldReg(self,reg_addr,reg_conf)
            else:
                print "WARNING: No type specified for {:#04x}".format(reg_addr)
                self.registers[name] = I2CRegister(self.bus,reg_addr,reg_conf)
                
    def __str__(self):
        return "I2C device at {}-{:#04x} '{}'".format(
                self.busnum, self.address, self.config['name'] )


class I2CRegister(object):
    def __init__(self, device, address, config):
        self.address = address  # register address
        self.read_byte = lambda byte: device.read_byte(self.address+byte)
        self.write_byte = lambda byte,value: device.write_byte(self.address+byte, value)
        self.config = config

    def read(self):
        print "WARNING: not implemented"
        return 0x00

    def write(self):
        print "WARNING: not implemented"
    
    def __str__(self):
        return "I2C register {:#04x} '{}'".format(
                self.address,self.config['name'])

class IntReg(I2CRegister):
    """ 8, 6, and 32 bit signed ints """
    def __init__(self, bus, addr, conf, signed = True):
        I2CRegister.__init__(self, bus, addr, conf)
        if signed:
            self.bits = int(conf['type'][3:]) # type is intX or intXY
        else:
            self.bits = int(conf['type'][4:]) # type is uintX or uintXY
        self.bytes = self.bits/8
        self.signed = signed

    def read(self):
        value = 0
        for i in reversed(range(self.bytes)):
            value <<= 8
            value += self.read_byte(byte=i)
        # test highest bit
        if self.signed and value >> (self.bits-1):
            # two's compliment
            value -= (1<<self.bits)
        return value

    def write(self, value):
        if self.signed:
            value += (1<<self.bits)  # two's copmliemnt
        for i in range(self.bytes):
            self.write_byte(byte=i, value=value & 0xff)
            value >>= 8
            
class BitfieldReg(I2CRegister):

    def __init__(self, bus, addr, conf):
        I2CRegister.__init__(self, bus, addr, conf)

