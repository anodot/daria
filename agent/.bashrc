function destination_logs { cat /sdc-data/logs/sdc.log | grep -A 5 RequestLogger; }

alias ll="ls -l"
alias clean="python /usr/src/app/src/agent/scripts/clean.py"
alias asc="agent source create"
alias asl="agent source list"
alias apc="agent pipeline create"
alias apu="agent pipeline update"
alias apl="agent pipeline list"
