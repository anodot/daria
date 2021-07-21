FROM python:3

WORKDIR /usr/src/app

RUN apt update && apt install nano

RUN adduser worker && chown worker -R ./
USER worker

COPY --chown=worker:worker ./ ./
RUN pip install --no-cache-dir --user -r requirements.txt

EXPOSE 1161/udp
CMD [ "python", "/home/worker/.local/bin/snmpsimd.py", "--data-dir=/usr/src/app/data", "--agent-udpv4-endpoint=0.0.0.0:1161" ]
