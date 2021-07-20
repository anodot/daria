FROM python:3

WORKDIR /usr/src/app

RUN adduser worker && chown worker -R ./
USER worker

COPY --chown=worker:worker requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

RUN wget https://github.com/etingof/snmpsim/archive/refs/heads/master.zip && unzip master.zip && mv snmpsim-master/data ./ && rm -r snmpsim-master && chmod 777 -R ./data

EXPOSE 1161/udp
CMD [ "python", "/home/worker/.local/bin/snmpsimd.py", "--data-dir=/usr/src/app/data", "--agent-udpv4-endpoint=0.0.0.0:1161" ]
