function destination_logs { cat /sdc-data/logs/sdc.log | grep -A 5 RequestLogger; }

alias ll="ls -l"
alias clean="python /usr/src/app/src/agent/scripts/clean.py"
