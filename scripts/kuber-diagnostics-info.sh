POD=$(kubectl get pod -l app.kubernetes.io/name=anodot-agent -o jsonpath="{.items[0].metadata.name}")
dest_path="./agent-diagnostics-info"
[ ! -d $dest_path ] && mkdir $dest_path
flags=""
[ -n "$1" ] && [ $1 == '--plain-text-credentials' ] && flags="--plain-text-credentials"

echo "Exporting configs"
kubectl exec $POD -- agent streamsets export --dir-path=/tmp/streamsets
kubectl cp $POD:/tmp/streamsets $dest_path/ && kubectl exec $POD -- rm -r /tmp/streamsets
echo "Copied to the $dest_path"
echo "Deleted /tmp/streamsets"
kubectl exec $POD -- agent source export --dir-path=/tmp/sources $flags
kubectl cp $POD:/tmp/sources $dest_path/ && kubectl exec $POD -- rm -r /tmp/sources
echo "Copied to the $dest_path"
echo "Deleted /tmp/sources"
kubectl exec $POD -- agent pipeline export --dir-path=/tmp/pipelines
kubectl cp $POD:/tmp/pipelines $dest_path/ && kubectl exec $POD -- rm -r /tmp/pipelines
echo "Copied to the $dest_path"
echo "Deleted /tmp/pipelines"

echo "Exporting logs"
log_path=$(kubectl exec $POD -- bash -c 'echo "$LOG_FILE_PATH"') && kubectl cp $POD:$log_path $dest_path/agent.log
echo "Exported agent application logs to the $dest_path/agent.log"
kubectl logs $POD >&$dest_path/agent-container.log
echo "Exported anodot-agent logs to the $dest_path/agent-container.log"
kubectl get pods -o custom-columns=":metadata.name" | grep streamsets-agent | while read -r pod; do
  kubectl logs $pod >&$dest_path/$pod.log
done
echo "Exported streamsets logs to the ./agent-diagnostics-info/ directory"

info_file=$dest_path/system_info.txt
touch $info_file
echo "Average load" >>$info_file
kubectl exec $POD -- cat /proc/loadavg >>$info_file
echo "" >>$info_file
kubectl exec $POD -- lscpu | grep 'CPU(s):' >>$info_file
echo "" >>$info_file
echo "Memory usage in MB" >>$info_file
kubectl exec $POD -- free -m >>$info_file
echo "Exported system info to the $info_file"

kubectl get pod $POD -o yaml >$dest_path/agent-container-info.yaml
echo "Exported agent pod info to the $dest_path/agent-container-info.yaml"
echo "Exporting streamsets pods info"
kubectl get pods -o custom-columns=":metadata.name" | grep streamsets-agent | while read -r pod; do
  kubectl get pod $pod -o yaml >$dest_path/$pod-container-info.yaml
done

echo "Archiving"
tar -cvf agent-diagnostics-info.tar $dest_path
rm -r $dest_path

echo "Exported anodot-agent diagnostics info to the agent-diagnostics-info.tar archive"
