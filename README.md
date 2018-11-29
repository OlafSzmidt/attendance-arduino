# Arduino Requirements

You might need to give system rights to the serial port that you are running the arduino on. This is system dependant. On ubuntu this might be: `sudo chmod a+rw /dev/ttyACM0` where `/dev/ttyACM0` is replaced with the serial port desired.

## For the NFC:

- Download [this zip file](http://goo.gl/F6beRM) and extract four folders into Arduino libraries. These folders are as follows: PN532, PN532_SPI, PN532_I2C and PN532_HSU
- Download [this zip file too](http://goo.gl/ewxeAe) and extract into libraries. Rename the folder to "NDEF".
- Change the `if 0` at the top of the NDEF readTag example to `if 1` and start coding.

## For the WiFi Shield:

-
