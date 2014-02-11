#!/usr/bin/env python

import time
import os, sys
topdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(topdir)
import i2c_device

dev = i2c_device.I2CDevice(1,0x19,config=topdir+'/sample_configs/lsm303dlhc_accel_i2c.yaml')
print "Device:", dev
print "Multi-byte read is:", dev.multi
print

ctrl1 = dev.registers['CTRL_REG1_A']
print "Register: ", ctrl1
print "Read: {:08b}".format( ctrl1.read_byte() )
print "Setting data rate:"
ctrl1.write('ODR','10Hz')
print "Read: {:08b}".format( ctrl1.read_byte() )
print "Setting enable flags:"
ctrl1.write('Xen','Enabled')
ctrl1.write('Yen','Enabled')
ctrl1.write('Zen','Enabled')
print "Read: {:08b}".format( ctrl1.read_byte() )
print

ctrl4 = dev.registers['CTRL_REG4_A']
print "Register: ", ctrl4
print "Read: {:08b}".format( ctrl4.read_byte() )
print "Setting Hi-res mode:"
ctrl4.write('HR','Enabled')
print "Read: {:08b}".format( ctrl4.read_byte() )
print

t0 = time.time()
while True:
  elapsed = time.time() - t0
  x = dev.registers['OUT_X_A'].read()
  y = dev.registers['OUT_Y_A'].read()
  z = dev.registers['OUT_Z_A'].read()
  print "[{:8.3f}] x: {:+06}, y: {:+06}, z: {:+06}".format(elapsed, x,y,z)
  time.sleep(0.1)



