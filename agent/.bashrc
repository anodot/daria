function destination_logs { cat /sdc-data/logs/sdc.log | grep -A 5 RequestLogger; }

alias ll="ls -l"
