import os
from datetime import datetime
from time import sleep

hour = input('hour\n')
minute = input('\nminute\n')
second = input('\nsecond\n')
ringtone = input('\nset ringtone\n')

now = datetime.now().timetuple()
sec_to_doom = (second-now.tm_sec)
min_to_doom = (minute-now.tm_min) - (1 if sec_to_doom < 0 else 0)
sec_to_doom %= 60
hrs_to_doom = (hour-now.tm_hour) - (1 if min_to_doom < 0 else 0 )
min_to_doom %= 60
state = 1 if hrs_to_doom < 0 else 0
hrs_to_doom %= 24

print "alarm set for", hrs_to_doom, "hours", min_to_doom, "minutes",sec_to_doom,'seconds\n'

sleep((hrs_to_doom*3600)+(min_to_doom*60)+sec_to_doom)

os.system("vlc --qt-start-minimized \"" + ringtone + "\"")
