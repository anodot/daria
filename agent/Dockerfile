FROM python:3.7

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt && python setup.py install && echo ". /usr/src/app/pipeline-complete.sh" >> /root/.bashrc

CMD ["bash"]
