FROM python:3.7

WORKDIR /usr/src/app

COPY . .

VOLUME /usr/src/app/data
ENV DATA_DIR '/usr/src/app/data'

ENV STREAMSETS_USERNAME admin
ENV STREAMSETS_PASSWORD admin
ENV STREAMSETS_URL 'http://localhost:18630'
ENV LOG_FILE_PATH '/var/log/agent.log'
ENV ANODOT_API_URL 'http://api.anodot.com'
ENV SDC_DATA_PATH: '/sdc-data'

RUN pip install --upgrade pip && pip install -r requirements.txt && python setup.py install && echo ". /usr/src/app/agent-complete.sh" >> /root/.bashrc

CMD ["bash"]
