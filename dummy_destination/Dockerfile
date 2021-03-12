FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV FLASK_APP="/usr/src/app/src/agent/api/main.py" FLASK_DEBUG=1

CMD flask run --host=0.0.0.0 --port=80
