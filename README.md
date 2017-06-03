Water_bath
==========

See http://lukemiller.org/index.php/2013/07/stupid-water-bath-tricks/ for more explanation of this script.

Control a Cole-Parmer digital Polystat water bath. This applies to older blue Polystat Digital waterbaths that 
were sold in the 2000's. This doesn't apply to current (2013) models, which use a different command structure.

Written under Python 2.7, requires the Pyserial package along with the built-in time and sys packages. 

This script lets the user run a linear temperature ramp (up or down) from a starting temperature. There are two
options: 1. bring the water bath to a set starting temperature, hold there until the user chooses to start the ramp,
or 2. start the ramp immediately from the current water bath temperature. All user input temperatures should be in
degrees Celsius, and the temperature ramp rate should be specified in degrees C per hour. 


