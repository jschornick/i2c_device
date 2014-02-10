import smbus
import yaml
from i2c_register import I2CRegister

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
        #print "Reading at bit", bit, "(length = %d)" % length
        byte = self.read_byte()
        #print "Raw byte:", bin(byte)
        lowbit = bit-length+1
        value = (byte>>lowbit) & ((1<<length)-1)
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
