I2C Device
==========

Let's say your new fancy-schmancy accelerometer just came in the mail from
_Bob's Sensor World_, and you're ready to start pulling data off that bad boy.
You shopped carefully, and you know that your sensor supports I2C, so you load
up the python-smbus library.  In a few short minutes, you're pulling off data.
What could be better?

I love the convenience of I2C as much as the next guy, but compared to the
quick victory describe above, the next few hours of hacking are usually not
nearly so fun.  If there is no existing library for your sensor, the next step
is all too often writing one from scratch... digging into page after page of 
interface specs described in the device datasheet.

Wouldn't it be nice if all those PDF tables of control registers could 
magically become a nice tidy Python object?  While that may never happen, 
this is the next best thing.  the I2C Device library imports a YAML-formatted
configuration for your device, and returns an well-behaved Python object 
for your device.  


Example
-------

```
In [1]: import i2c_device

In [2]: mydevice = i2c_device.I2CDevice(bus=1,address=0x19,config='lsm303dlhc_accel_i2c.yaml')

In [3]: mydevice.name
Out[3]: 'LSM303DLHC 3D accelerometer and 3D magnetometer'

In [4]: mydevice.registers
Out[4]: 
{'CTRL_REG1_A': <i2c_device.i2c_device.BitfieldReg at 0xb64f32f0>,
 'OUT_X_A': <i2c_device.i2c_device.IntReg at 0x68bfd0>,
 'OUT_Y_A': <i2c_device.i2c_device.IntReg at 0x68b3d0>,
 'OUT_Z_A': <i2c_device.i2c_device.IntReg at 0x68b4d0>,
 ...
 }

In [5]: ctrl_reg = mydevice.registers['CTRL_REG1_A']

In [6]: ctrl_reg.write('ODR','10Hz')

In [7]: ctrl_reg.write('Xen','Enabled')

In [8]: mydevice.registers['OUT_X_A'].read()
Out[8]: 13312
```


Configuration Files
-------------------

The repository includes a few sample configuration files as examples.  At this
early stage in the game, you'll have to spend the time to write your own for
each new device.  Of course, once someone takes the time to YAMLify the data
hidden within each device's datasheet, the library of configs will quickly
grow.  

There is a good chance that some of my initial choices for the YAML structure
are suboptimal or unintentionally limiting.  I'd like to believe we can
maintain a certain amount of clarity/conciseness in the format while still
supporting the diversity of I2C devices available.  The best way to find out is
to start populating the libray of devices and see what problems arise.  


Requirements
------------

`I2C_Device` is a layer on top of the lower level I2C/smbus library, which is
itself a Python wrapper around a the C smbus library.  The python library
comes in two flavors: the original C-extension (`python-smbus`) or the newer
PyPy-compatible CFFI version (`smbus-cffi`).

The original extension is faster and has been tested against more thoroughly.
Most distributions include this as "python-smbus" in their package 
repositories, or it is available here:

  http://www.lm-sensors.org/browser/i2c-tools/trunk/py-smbus/

If you want to try smbus-cffi instead, it is availble on PyPI.  

