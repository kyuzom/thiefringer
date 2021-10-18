#!/bin/sh
rsync -ave ssh --stats --exclude={"/dev/*","/proc/*","/sys/*","/run/*","/mnt/*","/media/*","/lost+found"} root@<IP-of-alarm-node>:/ /tmp/alarm/ --delete
cd /tmp
tar --warning="no-file-ignored" -cf alarm.tar alarm
gzip -c alarm.tar > alarm.tar.gz
rm -rf alarm/
rm -f alarm.tar
