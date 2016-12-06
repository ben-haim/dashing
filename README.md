Dashing 1.0.0
=============

Dashing is a project that displays stock graphs, ticker information, and market headlines in a fullscreen dashboard that is designed for use either on a Raspberry Pi or on desktop Linux.


How to install on Raspberry Pi
------------------------------

**1)** Create a fresh Raspbian Lite SD card.  Download from here:

https://www.raspberrypi.org/downloads/raspbian/

On Linux, extracting and installing to an SD card is just a few commands:

    # sha1sum 2016-11-25-raspbian-jessie-lite.zip

Verify the SHA-1 checksum with the download screen above, then:

    # unzip 2016-11-25-raspbian-jessie-lite.zip
    # dd if=2016-11-25-raspbian-jessie-lite.img of=<sd_card_reader_device>

On Windows or MacOS, follow these steps:

https://www.raspberrypi.org/documentation/installation/installing-images/README.md

**2)** Put the SD card into the system, make sure you are connected to the internet with an ethernet cord, then boot your Raspberry Pi.  Login as the "pi" user with password "raspberry".

**3)** Start a root shell:

    $ sudo -s

**4)** Update the system:

    # apt-get update
    # apt-get dist-upgrade

**5)** Install required packages for Dashing to work correctly:

    # apt-get install git lightdm openbox python-feedparser python-matplotlib python-pil python-pil.imagetk python-pycurl python-tk unclutter x11-xserver-utils

**6)** Enable lightdm (the lightweight desktop manager):

    # systemctl enable lightdm

**7)** Disable networking tools that will mess with the open WiFi scripts if you intend to have your Pi connect to any open WiFi.  If you are intending to use a wired connection or manually configure a private WiFi, skip this step.

    # systemctl disable networking
    # systemctl disable dhcpcd

**8)** Edit /etc/lightdm/lightdm.conf and change the following values, they are probably commented or set to something else, you can use vi or nano for this:

    autologin-user-timeout=0
    user-session=openbox

**9)** Exit your root shell:

    # exit

**10)** Ensure you are in your home directory:

    $ cd /home/pi

**11)** Clone the Dashing repository into your home directory:

    $ git clone https://github.com/BCable/dashing.git

**12)** Create the openbox configuration directory:

    $ mkdir /home/pi/.config/openbox

**13)** Edit or create /home/pi/.config/openbox/rc.xml with nano or vi, and set the contents to:

    <openbox_config>
        <applications>
            <application class="Dashing">
                <decor>no</decor>
                <maximized>yes</maximized>
            </application>
        </applications>
    </openbox_config>

**14)** Edit or create /home/pi/.config/openbox/autostart with nano or vi, and set the contents to the following.  Note, if you are intending this device to be wired instead of wireless, remove the first line:

    sudo bash /home/pi/dashing/open_wifi_connect.sh &
    xset -dpms
    xset s noblank
    xset s off
    xsetroot -bg "#000000"
    unclutter -noevents -grab &
    python /home/pi/dashing/dashing.py &

**15)** Reboot your Raspberry Pi and wait until the device connects and starts up.


Configuration File
------------------

The configuration file (dashing.conf) follows standard Python [ConfigParser](https://docs.python.org/2/library/configparser.html) syntax.

Available sections/options are:

    [general]
    data_points = 100

data_points tells how many data points that the graphs will retain.  If you are on desktop linux you can easily increase this, but on a Raspberry Pi you have to consider memory limitations.  This default seems to work pretty well for Raspberry Pi.

    [headlines]
    feeds0 = NAME::http://link.to/xml_feed

The headlines provided on the ticker can be configured by specifying RSS/ATOM feed links here.  Preferably, keep these HTTP if you are using the wireless option, since some wireless networks don't allow HTTPS on them.  The NAME is optional, and you can drop the "::" separator if you wish to use the default title found in the feed itself on the headline ticker.

Each feed must be named in numerical order named "feeds0", "feeds1", etc.

    [stocks]
    tickers0 = NAME::SYMBOL

This is in the format of the name for the stock as displayed, and the symbol associated with the data.  You can look up symbols on [Yahoo Finance](https://finance.yahoo.com/), since Dashing uses the Yahoo Finance API.

Each symbol must be named in numerical order named "tickers0", "tickers1", etc.  You should configure an amount of symbols that can create an even grid (5x5, 4x5, 6x6, 8x8, 8x7, etc), otherwise the display will look strange.


Usage with Desktop Linux
------------------------

This is more for debugging purposes or if you just want to run this by hand.

Using Fedora or Enterprise Linux packages.  The required packages to install are:

    # dnf install python-feedparser python-matplotlib python-matplotlib python-matplotlib-tk python-pillow python-pillow-tk python-pycurl

Using Debian or Ubuntu packages, these are very similar to the ones in the Raspbian install since it is essentially just Debian anyway:

    # apt-get install python-feedparser python-matplotlib python-pil python-pil.imagetk python-pycurl python-tk

After the required packages are installed, you can start the script from a cloned repository with a simple:

    $ python dashing.py
