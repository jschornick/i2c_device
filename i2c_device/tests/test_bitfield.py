from unittest import TestCase

import sys
from mock import Mock

from i2c_device import I2CDevice

class TestInit(TestCase):

    def setUp(self):
        try:
            self.i2c = I2CDevice(0,0x01,config='tests/test.yaml')
        except:
            pass
        self.bits = self.i2c.registers['TestBitfield'].bits
        self.bit_names = self.i2c.registers['TestBitfield'].bit_names

    def test_read_bit_config(self):
        self.assertEqual(len(self.bits), 3)

    def test_bit_name_map(self):
        bitnum = 0
        name = self.bits[bitnum]['name']
        self.assertIn(name, self.bit_names)
        self.assertEqual(self.bit_names[name], bitnum)

class TestRead(TestCase):

    def setUp(self):
        self.i2c = I2CDevice(0,0x01,config='tests/test.yaml')

    def set_mock_value(self, val):
        self.i2c.read_byte = Mock(return_value = val)

    def test_mock(self):
        fake_val = 0b10101101
        self.set_mock_value(fake_val)
        self.assertEqual(self.i2c.read_byte(), fake_val)
        self.assertNotEqual(self.i2c.read_byte(), fake_val+1)

    def test_read(self): 
        reg = self.i2c.registers['TestBitfield']

        self.set_mock_value(0b10101101)
        self.assertEqual(reg.read(0), 1)  # the single LSB
        self.assertEqual(reg.read(2), 0b10)  # two-bit value at bits 2 and 1
        self.assertEqual(reg.read(7), 0b1010)  # four-bit value at bits 7 to 4

        self.set_mock_value(0b00010110)
        self.assertEqual(reg.read(0), 0) 
        self.assertEqual(reg.read(2), 0b11)
        self.assertEqual(reg.read(7), 0b0001)

    def test_read_by_name(self): 
        reg = self.i2c.registers['TestBitfield']
        self.set_mock_value(0b10101101)
        self.assertEqual(reg.read('FourBits'), 0b1010)

class TestWrite(TestCase):

    def setUp(self):
        self.i2c = I2CDevice(0,0x01,config='tests/test.yaml')
        self.i2c.write_byte = Mock()

    def set_mock_value(self, val):
        self.i2c.read_byte = Mock(return_value = val)

    def test_mock(self):
        self.i2c.write_byte.reset_mock()
        self.i2c.write_byte(0b10101101)
        self.i2c.write_byte.assert_called_once_with(0b10101101)

    def test_merged_write(self):
        reg = self.i2c.registers['TestBitfield']
        self.set_mock_value(0b10101101)
        addr = reg.address

        self.i2c.write_byte.reset_mock()
        bitnum = 0
        reg.write(bitnum,0)
        self.i2c.read_byte.assert_called_once()  # should read since merging
        self.i2c.write_byte.assert_called_once_with(addr,0b10101100)

        self.i2c.write_byte.reset_mock()
        bitnum = 2
        reg.write(bitnum,0b01)
        self.i2c.write_byte.assert_called_once_with(addr,0b10101011)

        self.i2c.write_byte.reset_mock()
        bitnum = 7
        reg.write(bitnum,0b1011)
        self.i2c.write_byte.assert_called_once_with(addr,0b10111101)
       
    def test_masked_write(self):
        reg = self.i2c.registers['TestMaskedBitfield']
        self.set_mock_value(0b10101100)
        addr = reg.address

        self.i2c.write_byte.reset_mock()
        reg.write(bit=0,value=1)
        self.i2c.write_byte.assert_called_once_with(addr,0b00001101)

        self.i2c.write_byte.reset_mock()
        reg.write(bit=7,value=0b0101)
        self.i2c.write_byte.assert_called_once_with(addr,0b00001100)

