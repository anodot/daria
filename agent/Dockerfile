FROM tiangolo/uwsgi-nginx-flask:python3.8

#defined in jenklins build, so for any local build it should be explicitly set as following:
#docker build --build-arg GIT_SHA1=$(git describe --tags --dirty --always)
ARG GIT_SHA1=local-build

WORKDIR /usr/src/app

COPY . .
COPY .bashrc /root/.bashr
COPY ./custom_entrypoint.sh /
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY nginx.conf /etc/nginx/nginx.conf
COPY uwsgi-nginx-entrypoint.sh /uwsgi-nginx-entrypoint.sh
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini

RUN chmod +x /custom_entrypoint.sh /uwsgi-nginx-entrypoint.sh

ENV SDC_CONF_PARSER_LIMIT="20048576" STREAMSETS_USERNAME="admin" STREAMSETS_PASSWORD="admin" \
    STREAMSETS_URL="http://localhost:18630"

ENV LOG_FILE_PATH="/var/log/agent.log" ANODOT_API_URL="https://api.anodot.com" ENV_PROD='true' VALIDATION_ENABLED="true"

ENV LISTEN_PORT 8080
EXPOSE 8080

RUN ./install_requirements.sh
RUN python setup.py install && echo ". /usr/src/app/agent-complete.sh" >> /root/.bashrc

RUN cd /usr/local/src && wget https://www.openssl.org/source/openssl-1.0.2k.tar.gz && tar xvf openssl-1.0.2k.tar.gz && cd openssl-1.0.2k/ && ./config --prefix=/usr/local/openssl-1.0.2k && make && make install

ENTRYPOINT ["/custom_entrypoint.sh"]
CMD ["/start.sh"]
