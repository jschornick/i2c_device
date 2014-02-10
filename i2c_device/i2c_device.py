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
            if not address in self.config['addresses']:
                print "WARNING: address {:#04x} not valid for config!".format(address)
            self.process_config(self.config)

    def process_config(self, config):
        self.name = config['name']
        self.registers = {}
        for reg_addr,reg_conf in config['registers'].items():
            name = reg_conf['name']
            try:
                reg_type = reg_conf['type']
            except KeyError:
                reg_type = None
            if reg_type in ['int8', 'int16', 'int32']:
                self.registers[name] = IntReg(self,reg_addr,reg_conf)
            elif reg_type in ['uint8', 'uint16', 'uint32']:
                self.registers[name] = IntReg(self,reg_addr,reg_conf,signed=False)
            elif reg_type == 'bitfield':
                self.registers[name] = BitfieldReg(self,reg_addr,reg_conf)
            elif reg_type == 'string':
                self.registers[name] = StringReg(self,reg_addr,reg_conf)
            else:
                print "WARNING: No type specified for {:#04x}".format(reg_addr)
                self.registers[name] = I2CRegister(self.bus,reg_addr,reg_conf)
                
    def read_byte(self, register):
        #print "Reading addr:", self.address, ", reg:", register
        return self.bus.read_byte_data(self.address, register)

    def write_byte(self, register, value):
        return self.bus.write_byte_data(self.address, register, value)

    def __str__(self):
        return "I2C device at {}-{:#04x} '{}'".format(
                self.busnum, self.address, self.config['name'] )


class I2CRegister(object):
    def __init__(self, device, address, config):
        self.address = address  # register address
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

# TODO: make into properties if we can still call write_val()
class IntReg(I2CRegister):
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

class BitfieldReg(I2CRegister):

    def __init__(self, bus, addr, conf):
        I2CRegister.__init__(self, bus, addr, conf)
        if 'writemask' in self.config.keys():
            self.mask = self.config['writemask']
        else:
            self.mask = 0xff
       
        self.map_bit_names()

    def map_bit_names(self):
        """ Build reverse map names of bits and remap each bit's value dict """
        self.bits = self.config['bits']
        self.bit_names = {}
        for bitnum,bit in self.bits.items():
            # create a name -> bitnum mapping
            if 'name' in bit.keys():
                self.bit_names[bit['name']] = bitnum
            # reverse map a subfields possible bit values when provided with names
            if 'values' in bit.keys():
                bit['value_names'] = {}
                for value_num,val_name in bit['values'].items():
                    bit['value_names'][val_name] = value_num

    def read(self,bit):
        """ Read bit at postion bit, or position defined by named bit """
        if type(bit) is str:
            bit = self.bit_names[bit]
        length = self.bits[bit]['length']
        print "Reading at bit", bit, "(length = %d)" % length
        byte = self.read_byte()
        print "Raw byte:", bin(byte)
        value = (byte>>bit) & ((1<<length)-1)
        return value

    def write(self, bit, value, merge=True):
        """ 
        Write value starting at position bit (high to low)

        When merge is set, first read the current value so that only the
        specified bits will be changed.

        """
        if type(bit) is str:
            bit = self.bit_names[bit]
        if type(value) is str:
            value = self.bits[bit]['value_names'][value]
        length = self.bits[bit]['length'] 
        lowbit = bit-length+1
        print "Writing {:08b} on bits {} to {})".format(value, bit, lowbit)
        new = value << lowbit
        # merge the new with the old
        if merge:
            old = self.read_byte()
            mergemask = ((1<<length)-1) << lowbit
            print "Merging {:08b} with {:08b} using mask {:08b}".format(new, old, mergemask)
            # clear bits in old and OR in the new ones
            new = (old & (0xff ^ mergemask)) | new
        new &= self.mask
        print "Masked with {:08b} => {:08b}".format(self.mask, new)
        self.write_byte(new)

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

