#!/bin/bash

#set -e
#set -u
#
#service cron start
#
#touch /etc/cron.d/cron
#echo "* * * * * python /usr/src/app/src/agent/scripts/send_to_bc.py" > /etc/cron.d/cron
#chmod 0644 /etc/cron.d/cron
#crontab /etc/cron.d/cron

exec /entrypoint.sh "$@"
