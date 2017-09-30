#! /bin/bash

# Placeholder

# Example crontab:
# * * * * * /home/pi/fwintel/fwintel.sh debug > /home/pi/fwintel/errors.txt


do_start () {
    /usr/bin/python3 "/home/pi/fwintel/fwintel.py" > /dev/null &
}
do_start_debug () {
    cd "/home/pi/fwintel/"
    python3 "fwintel.py"
}

case "$1" in
  start)
    do_start
    ;;
  debug)
    do_start_debug
    ;;
  stop)
    exit 0
    ;;
  *)
    exit 1
    ;;
esac
exit 0
