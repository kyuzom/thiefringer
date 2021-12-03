# thiefringer

ThiefRinger - alarm system.

Threads like microservices - They running simultaneously and communicate via Queue.
Queue like a message bus.

## Installation

### libs

Install extra libraries that this package depends on:
``` sh
opkg install python-light python-setuptools pyOnionGpio pyOledExp power-dock2
# clone and install https://github.com/kyuzom/gpydem
pip install gpydem
```

### pip

Install this package via **pip** package manager:
``` sh
pip install thiefringer
```

### setup.py

Install this package manually via **setup.py** file:
``` sh
git clone https://github.com/kyuzom/thiefringer
cd thiefringer
python setup.py install
```

## Configuration

Config file is used to determine custom behavior a.k.a. client-side logic.
It is JSON formatted.

Parameters:
``` text
  {
      PIR [map] - PIR motion detector related configurations, default: {}
      {
          pin          [int] - GPIO pin number,                          default: -1
          active_value [str] - GPIO logic value when motion is detected, default: "0"
          alarm        [map] - Alert message related configurations, default: {}
          {
              number  [str] - Phone number, default: ""
              message [str] - SMS Message,  default: "ALERT"
          }
      }
      GSM [map] - GSM 3G USB modem related configurations, default: {}
      {
          modem_type [str]   - GSM modem type Id,                             default: ""
          dev_id     [str]   - GSM modem character device (serial port Id),   default: "/dev/ttyS0"
          baudrate   [int]   - GSM modem BaudRate (serial port speed),        default: 9600
          PIN        [str]   - SIM card PIN code,                             default: ""
          re_timeout [float] - GSM modem timeout to reboot (after PIN setup), default: 1.0
      }
  }
```

## Usage

### cmd line

Run when your config file *.thiefringer.json* is next to your python script:
``` sh
python /path/to/thiefringer.py
```

Run with specify path manually to your config file:
``` sh
python /path/to/thiefringer.py -c /path/to/.thiefringer.json
```

### daemon

**NOTE!** Additional files can be found under the [init.d](system/etc/init.d) directory.

Prepare **Procd** init system files on an OpenWrt system, then start in the background, then enable it:
``` sh
/etc/init.d/thiefringer start
/etc/init.d/thiefringer enable
```

## Board

Onion Omega2 Pro - board specific notes and guidelines.

### opkg

Edit the repository source file to access additional packages:
``` sh
vi /etc/opkg/distfeeds.conf
```

Guide what to do manually via the default text editor **Vi**:
``` text
i
uncomment -> src/gz openwrt_base http://downloads.openwrt.org/releases/18.06-SNAPSHOT/packages/mipsel_24kc/base
escape
:x
```

Then install any additional package you want:
``` sh
opkg update
opkg install nano mc
```

### pivot-overlay

**Booting from External Storage**

Prepare the system with the necessary additional packages:
``` sh
opkg update
opkg install swap-utils block-mount e2fsprogs
```

Pack the FileSystem into a separate place aka **External Storage**, therefore from now on it will boot from there:
``` sh
tar -C /overlay -cvf - . | tar -C /mnt/mmcblk0p1 -xf -
block detect > /etc/config/fstab
```

Edit the **fstab** file to change the location of your FileSystem:
``` sh
nano /etc/config/fstab
```

Guide what to do manually via your favorite text editor **nano**:
``` text
replace -> option  target  '/mnt/mmcblk0p1' -> option  target  '/overlay'
replace -> option  enabled '0' -> option  enabled '1'
ctrl+x
y
```

Restart the system:
``` sh
reboot
```

### turn off LEDs

Put these lines at the end of your ***/etc/rc.local*** file:
``` sh
# Turn off full-color LED
omega2-ctrl gpiomux set uart2 pwm23
echo -en '\x00\x00\x00' > /dev/ledchain2
```

Make the script executable:
``` sh
chmod +x /etc/rc.local
```

## License

thiefringer is MIT licensed. See the included [LICENSE](LICENSE) file.
