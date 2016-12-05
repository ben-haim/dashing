#!/bin/bash

#
# Dashing - open_wifi_connect.sh
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: GPLv2
#


# blacklisting certain wifi hotspots (builds over time)
blacklist="xfinitywifi"

# gather interface info
mac_address="00:02:"$(python -c 'import random; print(":".join(
	[hex(random.randint(0,255))[2:] for i in range(0,4)]
))')
interface=$(iwconfig 2>&1 | grep IEEE | head -n 1 | cut -d ' ' -f1)

# set MAC address
ifconfig $interface hw ether $mac_address

# bring interface up
ifconfig $interface up

# test connection
function testcon(){
	if [[ ! -z "$(
		wget -q -O - "http://yahoo.com/" | grep "s.yimg.com"
	)" ]]; then
		echo -n 0
	else
		echo -n 1
		# make sure DHCP is killed if the connection is broken
		pkill dhclient
	fi
}

# loop forever, forever trying to connect to open wifi
for ((;;)); do
	if [[ "$(testcon)" = "0" ]]; then
		sleep 60
		break
	fi

	bss=""
	essid=""
	keybool=0
	for line in $(
		iw $interface scan 2>&1 |
		grep -E "(^BSS)|SSID|capability" |
		sed -r "s/^[ \t]+//g" | sed -r "s/^BSS/end\nBSS/g" |
		sed -r "s/[ ]+//g"
	); do
		# extract data from scan
		if [[ "${line:0:4}" = "SSID" ]]; then
			essid="${line:5}"
		elif [[ "${line:0:3}" = "BSS" ]]; then
			bss="${line:3:17}"
			essid=""
			keybool=0
		elif [[ ! -z "$(echo "$line" | grep -E "ESS.*Privacy")" ]]; then
			keybool=1
		fi

		# if still gathering info on same BSS, continue to next line
		if [[ "$line" != "end" ]]; then
			continue
		fi

		# if no encryption and not in blacklist, try it out
		if \
		[[ "$keybool" = "0" ]] && \
		[[ ! -z "$(echo $essid | grep -vE "$blacklist")" ]]; then
			# specify ESSID and AP
			iwconfig $interface essid $essid ap $bss
			# acquire DHCP config
			dhclient $interface
			# wait a bit
			sleep 1

			# see if it worked
			if [[ "$(testcon)" = "0" ]]; then
				# finish if success
				break
			else
				# add wifi to blacklist if fail
				blacklist="$blacklist|$essid"
			fi
		fi
	done

	sleep 5
done
