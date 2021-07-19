FROM python:3

RUN apt update && apt install -y snmp telnet netcat

RUN adduser worker
USER worker

WORKDIR /usr/src/app

COPY --chown=worker:worker requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

COPY ./snmpsim_data ./data

EXPOSE 11161
CMD [ "python", "/home/worker/.local/bin/snmpsimd.py", "--data-dir=/usr/src/app/data", "--agent-udpv4-endpoint=127.0.0.1:11161" ]
