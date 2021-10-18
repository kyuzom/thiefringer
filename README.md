# thiefringer

ThiefRinger - alarm system.

## Installation

### libs

Install extra libraries that this package depends on:
``` text
opkg install python python-pip pyOnionGpio pyOledExp power-dock2
```

### pip

Install this package via ***pip*** package manager:
``` text
pip install thiefringer
```

### setup.py

Install this package manually via ***setup.py*** file:
``` text
git clone https://github.com/kyuzom/thiefringer
cd thiefringer
python setup.py install
```

## Configuration

Config file is used to determine custom behavior aka client-side logic.
It is Json formatted.

Parameters:
``` text
  {
      motion [map] - Motion detection related configurations
      {
          pin          [int]   - GPIO pin number,                                  default: -1
          active_value [str]   - GPIO logic value when motion is detected,         default: "0"
          timeout_sec  [float] - Timeout of waiting for terminate signal in [sec], default: 0.1
      }
  }
```

## Usage

### cmd line

Run when your config file ***.thiefringer.json*** is next to your python script:
``` text
python /path/to/thiefringer.py
```

Run with specify path manually to your config file:
``` text
python /path/to/thiefringer.py -c /path/to/.thiefringer.json
```

### daemon

Additional files can  be found under the [init.d](system/etc/init.d) directory.

Prepare **Procd** init system files on an OpenWrt system, then start in the background, then enable it:
``` text
/etc/init.d/thiefringer start
/etc/init.d/thiefringer enable
```

## Board

Onion Omega2 Pro - board specific notes and guidelines.

### opkg

Edit the repository source file to access additional packages:
``` text
vi /etc/opkg/distfeeds.conf
```

Guide what to do manually via the default text editor ***Vi***:
``` text
i
uncomment -> src/gz openwrt_base http://downloads.openwrt.org/releases/18.06-SNAPSHOT/packages/mipsel_24kc/base
escape
:x
```

Then install any additional package you want:
``` text
opkg update
opkg install nano mc
```

### pivot-overlay

**Booting from External Storage**

Prepare the system with the necessary additional packages:
``` text
opkg update
opkg install swap-utils block-mount e2fsprogs
```

Pack the FileSystem into a separate place aka ***External Storage***, therefore from now on it will boot from there:
``` text
tar -C /overlay -cvf - . | tar -C /mnt/mmcblk0p1 -xf -
block detect > /etc/config/fstab
```

Edit the ***fstab*** file to change the location of your FileSystem:
``` text
nano /etc/config/fstab
```

Guide what to do manually via your favorite text editor ***nano***:
``` text
replace -> option  target  '/mnt/mmcblk0p1' -> option  target  '/overlay'
replace -> option  enabled '0' -> option  enabled '1'
ctrl+x
y
```

Restart the system:
``` text
reboot
```

### turn off LEDs

Put these lines at the end of your ***/etc/rc.local*** file:
``` text
# Turn off full-color LED
omega2-ctrl gpiomux set uart2 pwm23
echo -en '\x00\x00\x00' > /dev/ledchain2
```

Make the script executable:
``` text
chmod +x /etc/rc.local
```

## License

thiefringer is MIT licensed. See the included [LICENSE](LICENSE) file.
