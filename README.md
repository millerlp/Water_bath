Water_bath
==========

See http://lukemiller.org/index.php/2013/07/stupid-water-bath-tricks/ for more 
explanation of this script.

Control a Cole-Parmer digital Polystat water bath or an ANOVA A-series water
bath (added June 2017). 

## Cole-Parmer Polystat
For the Cole-Parmer Polystat, the code in `water_bath.py` applies to older
 blue Polystat Digital waterbaths that 
were sold in the 2000's. This doesn't apply to current (2013) models, which use 
a different command structure.

## ANOVA A-series
See the file `ANOVA_water_bath.py` for example code to run an ANOVA A-series
digital water bath (http://www.waterbaths.com).

============

For both types of water baths, you can interface with a computer using an old
Dsub 9-pin serial cable (RS232) and a USB-Serial adapter. I use a 
Chipi-X10 cable: http://www.ftdichip.com/Products/Cables/USBRS232.htm with Linux 
or Windows. 


Written under Python 2.7, requires the `pyserial` package along with the built-in 
`time`, `re`, and `sys` packages. 

This script lets the user run a linear temperature ramp (up or down) from a 
user-defined starting temperature. There are two
options: 1. bring the water bath to a set starting temperature, hold there until
 the user chooses to start the ramp,
or 2. start the ramp immediately from the current water bath temperature. All 
user input temperatures should be in
degrees Celsius, and the temperature ramp rate should be specified in degrees C 
per hour. 


