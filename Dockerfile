FROM python:3.7

WORKDIR /usr/src/app

COPY ./agent .

RUN pip install -r requirements.txt

CMD ["python", "agent.py"]
