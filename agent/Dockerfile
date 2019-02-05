FROM python:3.7

WORKDIR /usr/src/app

COPY . .

VOLUME /usr/src/app/data
ENV DATA_DIR '/usr/src/app/data'

RUN pip install --upgrade pip && pip install -r requirements.txt && python setup.py install && echo ". /usr/src/app/agent-complete.sh" >> /root/.bashrc

CMD ["bash"]
