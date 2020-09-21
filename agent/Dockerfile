FROM tiangolo/uwsgi-nginx-flask:python3.8

#defined in jenklins build, so for any local build it should be explicitly set as following:
#docker build --build-arg GIT_SHA1=$(git describe --dirty --always)
ARG GIT_SHA1=local-build

WORKDIR /usr/src/app

COPY . .
COPY .bashrc /root/.bashrc

VOLUME /usr/src/app/data

ENV SDC_CONF_PARSER_LIMIT="20048576" STREAMSETS_USERNAME="admin" STREAMSETS_PASSWORD="admin" \
    STREAMSETS_URL="http://localhost:18630" SDC_DATA_PATH="/sdc-data"

ENV LOG_FILE_PATH="/var/log/agent.log" ANODOT_API_URL="http://api.anodot.com" ENV_PROD='true' VALIDATION_ENABLED="true"

# flask app config
ENV UWSGI_INI="/usr/src/app/uwsgi.ini"

RUN pip install --upgrade pip && pip install -r requirements.txt && python setup.py install && echo ". /usr/src/app/agent-complete.sh" >> /root/.bashrc
RUN apt update && apt install -y vim netcat curl nano postgresql-client
