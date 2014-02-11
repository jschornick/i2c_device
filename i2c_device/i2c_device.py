import smbus
import yaml

from i2c_register import I2CRegister
from i2c_integer import IntegerReg
from i2c_string import StringReg
from i2c_bitfield import BitfieldReg

class I2CDevice(object):

    def __init__(self, bus, address, config=None):
        self.busnum = bus
        if bus is not None:
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

        # multi-byte read/write support
        try:
            self.multi = config['protocol']['multi']
        except KeyError:
            self.multi = False

        try:
            self.comm_base = config['command']['default']
        except KeyError:
            self.comm_base = 0

        self.registers = {}
        for reg_addr,reg_conf in config['registers'].items():
            name = reg_conf['name']
            try:
                reg_type = reg_conf['type']
            except KeyError:
                reg_type = None

            # Since reg_conf has a type, should we do this parsing in 
            # the generic Register class instead of here?
            if reg_type in ['int8', 'int16', 'int32']:
                self.registers[name] = IntegerReg(self,reg_addr,reg_conf)
            elif reg_type in ['uint8', 'uint16', 'uint32']:
                self.registers[name] = IntegerReg(self,reg_addr,reg_conf,signed=False)
            elif reg_type == 'bitfield':
                self.registers[name] = BitfieldReg(self,reg_addr,reg_conf)
            elif reg_type == 'string':
                self.registers[name] = StringReg(self,reg_addr,reg_conf)
            else:
                print "WARNING: No type specified for {:#04x}".format(reg_addr)
                self.registers[name] = I2CRegister(self.bus,reg_addr,reg_conf)
                
    def read_byte(self, register):
        comm = register | self.comm_base
        # TODO: how does this two call sequence compare to read_byte_data(reg,comm)?
        self.bus.write_byte(self.address, comm)  # tell the device what we want to read
        data = self.bus.read_byte(self.address)  # then read it
        return data

    # this doesn't work on dmcc!
    def read_word(self, register):
        # TODO: verify that devices needs auto_inc enabled for this to work
        #comm = register | self.auto_inc | self.comm_base
        comm = register | self.comm_base
        #print " Comm: {:08b}".format(comm)
        data = self.bus.read_word_data(self.address, comm)
        #print " Word: {:016b}".format(data)
        return data

    def write_byte(self, register, value):
        register |= self.comm_base
        return self.bus.write_byte_data(self.address, register, value)
       
    def __str__(self):
        return "I2C device at {}-{:#04x} '{}'".format(
                self.busnum, self.address, self.config['name'] )


