FROM python:3

RUN adduser worker
USER worker

WORKDIR /usr/src/app

COPY --chown=worker:worker requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

COPY ./snmpsim_data ./data

EXPOSE 161/udp
CMD [ "python", "/home/worker/.local/bin/snmpsimd.py", "--data-dir=/usr/src/app/data", "--agent-udpv4-endpoint=0.0.0.0:161" ]
