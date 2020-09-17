function get_errors { tail /sdc-data/errors/$1/$(ls -t /sdc-data/errors/$1 | head -1) | grep -oP '"errorMessage":.*?[^\\]",'; }

function destination_logs { cat /sdc-data/logs/sdc.log | grep -A 5 RequestLogger; }

alias ll="ls -l"
