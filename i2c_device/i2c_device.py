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
        return self.bus.read_byte_data(self.address, register)

    def write_byte(self, register, value):
        return self.bus.write_byte_data(self.address, register, value)

    def process_config(self, config):
        self.name = config['name']
        self.registers = {}
        for reg_addr,reg_conf in config['registers'].items():
            #self.registers[reg['name']] = I2CRegister(self.bus,self.address,reg)
            self.registers[reg_conf['name']] = I2CRegister(
                    self.read_byte,self.write_byte,reg_addr,reg_conf)

    def __str__(self):
        return "I2C device at {}-{:#04x} '{}'".format(
                self.busnum, self.address, self.config['name'] )

class I2CRegister(object):
    def __init__(self, reader, writer, address, config):
        #self.bus = bus
        self.reader = reader
        self.writer = writer
        self.address = address  # register address
        self.config = config
        try:
            self.regtype = config['type']
        except KeyError:
            print "WARNING: No type specified for register {:#04x}, assuming unsigned int8".format(address)

    def read(self):
        # TODO: move into separate functions instead of inline
        if self.regtype == 'int16':
            low = self.reader(self.address)
            high = self.reader(self.address+1)
            #if high & (1<<7):
            if (high >> 7):  # if highest bit set
                # two's compliment
                return low + (high<<8) - (1<<16)
            else:
                return low + (high<<8)
        elif self.regtype == 'int32':
            b0 = self.reader(self.address)
            b1 = self.reader(self.address+1)
            b2 = self.reader(self.address+2)
            b3 = self.reader(self.address+3)
            #if high & (1<<7):
            value = b0 + (b1<<8) + (b2<<16) + (b3<<24)
            if (b3 >> 7):  # if highest bit set
                # two's compliment
                value -= (1<<32)
            return value
        elif self.regtype == 'bitfield':
            print "Reading bitfield"
            return 0
        else:
            print "WARNING: Invalid register type"
            return 

    def write(self, value):
        if self.regtype == 'int16':
            value += (1<<16)  # two's compliment
            high = (value >> 8) & 0xff
            low = value & 0xff
            self.writer(self.address, low)
            self.writer(self.address+1, high)


    def __str__(self):
        return "I2C register {:#04x} '{}'".format(
                self.address,self.config['name'])
    
