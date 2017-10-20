# fwintel

##Disclaimer##

As of current writing, this is a very poorly documented intel bot designed for Factional Warfare.  It's published so that any may use or learn from this project; however if you want any functionality, it might be simpler to just EVE-mail Nikolai Agnon or contact Xadi#6094 on Discord, and I'll be happy to add your corp/alliance's discord.  

For context, I run this on a [Raspberry Pi Zero W](https://www.adafruit.com/product/3409) with an [OLED display](https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi).  *I'm working towards moving the OLED display bit away from the fwintel bot, because (realistically) nobody else has any use for it.*

An example of what this prints is as follows:
```
Highly contested systems (hourly):
M-Huola           47.3% (+1)
M-Tannakan        46.7% (-1)
M-Haras           46.0% (+2)
M-Sahtogas        45.3% (+2)

High-activity systems (hourly):
M-Turnur          32.7% (-5)
A-Sifilar         35.3% (+4)
M-Arzad           20.0% (-4)
M-Kourmonen       44.0% (-3)

Watchlisted systems (hourly):
M-Kamela          19.3% (+1)

Just in the past 31 minutes: (d-plexes, o-plexes, total)
Amarr (10) : 1 / 5 / 6
Minmatar (60): 9 / 7 / 16

Fri, 20 Oct 2017 09:51:10
Next update in 29 minutes
~~~~~
```

The settings.json file should be fairly self explanatory.  The hardest part is setting up a webhook - Discord has a step by step guide [available here](https://support.discordapp.com/hc/en-us/articles/228383668) that explains the basic process.

**Note that Slack support is being phased out.**  The bot began as a Slack bot originally, but I'm not in DNG any longer, and I think everyone who's actually still relevant has switched to the better platform.
