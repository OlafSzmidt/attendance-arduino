# Setup Instructions
The project uses [https://github.com/pypa/pipenv](pipenv), a tool for packaging
Python projects. The requirements are read from the `Pipfile` and `Pipfile.lock`
files. In order to install the dependencies first install pipenv, then run
`pipenv install`. Then run `pipenv shell` to open a virtual environment.

For security purposes, the Arduino and the portal (and its APIs) must run on
the same local network. Currently, the arduino is programmed to connect to a
WPA2_PSK network with the SSID `Attendance` and KEY `attendancesystem`. If you
want to change this, alter the details in `ReadTag/ReadTag.ino`.

To host a private network easily, you can tether from 3G/4G using a phone.

The arduino requires the buzzer to be connected at pin 9 and GND. It also requires
sufficient power. This can be either portable or a USB type B lead (printer cable)
can be used to power it.

In order to run the portal once the arduino is connected, run `python manage.py runserver [ip]`.
To determine the IP of the network, you can run `ip addr show` on Ubuntu or
equivalent its equivalent. Replace `[ip]` with this IP, at port `8000`. In my
case this is `python manage.py runserver 192.168.43.205:8000`. If your IP is
different, you also need to add it to `ALLOWED_HOSTS` in
`attendance_project/settings.py` file. This is again, for security.

If you want to start fresh, delete the `db.sqlite3` file and either run the server
again (and its migrations) or just copy a backup file from `db_backups`. I recommend
using the `starting.sqlite3` file - make sure you rename it to `db.sqlite3` and place
it at the correct location (ie. root of the folder `attendance-arduino`).

To listen to the output of the arduino, you can open the Arduino IDE and its
in built Serial Monitor. UART BAUD rate is set at 9600, so make sure you listen
at that rate. You may have to set the port and the device in the settings correctly
so that the IDE recognises your Arduino.
