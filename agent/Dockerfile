FROM python:3.7

WORKDIR /usr/src/app

COPY . .
ADD .bashrc /root/.bashrc

VOLUME /usr/src/app/data

ENV DATA_DIR="/usr/src/app/data" STREAMSETS_USERNAME="admin" STREAMSETS_PASSWORD="admin" STREAMSETS_URL="http://localhost:18630" \
    LOG_FILE_PATH="/var/log/agent.log" ANODOT_API_URL="http://api.anodot.com" SDC_DATA_PATH="/sdc-data"

RUN pip install --upgrade pip && pip install -r requirements.txt && python setup.py install && echo ". /usr/src/app/agent-complete.sh" >> /root/.bashrc

CMD ["bash"]
