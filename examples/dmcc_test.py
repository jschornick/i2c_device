#!/usr/bin/env python

import i2c_device
import time

dev = i2c_device.I2CDevice(1,0x2d,config='examples/dmcc_i2c.yaml')
print "Device: ", dev

reg = dev.registers['PowerMotor1']
print "Register: ", reg

print "Read from reg: ", reg.read()

num = 25
start = time.time()
for i in range(num):
    reg.read()
ms = (time.time() - start) *1000
print "Read {} 16-bit signed values in {:0.2f} ms, {:0.3f} ms/read".format(num,ms,ms/num)
print

print "Write positive to reg: "
reg.write(1500)
print "Read from reg: ", reg.read()
print
print "Write neg to reg: "
reg.write(-1500)
print "Read from reg: ", reg.read()
print
print "Write zero to reg: "
reg.write(0)
print "Read from reg: ", reg.read()
print

print "Battery voltage:", dev.registers['Voltage'].read()/1000.0
print
while True:
  #dev.registers['Execute'].write_val('Refresh')
  dev.registers['Execute'].write(0x00)
  print "QEI 1:", dev.registers['QEI1Velocity'].read()



