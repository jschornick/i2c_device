#!/usr/bin/env python

import time
import os, sys
topdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(topdir)
import i2c_device

dev = i2c_device.I2CDevice(1,0x19,config=topdir+'/sample_configs/lsm303dlhc_accel_i2c.yaml')
print "Device:", dev
print

ctrl = dev.registers['CTRL_REG1_A']
print "Register: ", ctrl
print "Read: {:08b}".format( ctrl.read_byte() )
print

print "Setting data rate:"
ctrl.write('ODR','10Hz')

print "Enabling via control register:"
ctrl.write('Xen','Enabled')
ctrl.write('Yen','Enabled')
ctrl.write('Zen','Enabled')

print "Register: ", ctrl
print "Read: {:08b}".format( ctrl.read_byte() )

t0 = time.time()
while True:
  elapsed = time.time() - t0
  x = dev.registers['OUT_X_A'].read()
  y = dev.registers['OUT_Y_A'].read()
  z = dev.registers['OUT_Z_A'].read()
  print "{:8.3f} x: {}, y: {}, z {}".format(elapsed, x,y,z)



