#!/usr/bin/env python

import time
import os, sys
import i2c_device

def read_data():
    valid = dev.registers['STATUS'].read('AVALID')
    c = dev.registers['CDATA'].read()
    r = dev.registers['RDATA'].read()
    g = dev.registers['GDATA'].read()
    b = dev.registers['BDATA'].read()
    print "V:{}  c: {}, r: {}, g: {} b: {}".format(valid,c,r,g,b)
    #return valid, c, r, g, b

dev = i2c_device.I2CDevice(1,0x29,config='tcs3472_i2c.yaml')
print "Device:", dev
print

enable = dev.registers['ENABLE']
print "Register: ", enable
print "Raw: {:08b}".format( enable.read_byte() )
print "AEN: {}".format( enable.read('AEN') )
print

id = dev.registers['ID']
print "Register: ", id
print "Read: {:#010x}".format( id.read_byte() )
print

status = dev.registers['STATUS']
print "Register: ", status
print "Raw: {:08b}".format( status.read_byte() )
print "AVALID: {}".format( status.read('AVALID') )

print "Enabling power via control register:"
enable.write('PON','Enable')
print "Enabling ADCs via control register:"
enable.write('AEN','Enable')

#enable.write('PON','Disable')

enable = dev.registers['ENABLE']
print "Register: ", enable
print "Read: {:08b}".format( enable.read_byte() )
print

t0 = time.time()
while True:
    elapsed = time.time() - t0
    print "[{:8.3f}] ".format(elapsed),
    read_data()
    time.sleep(0.1)
