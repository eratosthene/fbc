FROM tiangolo/uwsgi-nginx-flask:python3.10

RUN apt-get update \
  && apt-get install -y ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade -r /requirements.txt
RUN sed -i 's/int(pk)/str(pk)/g' /usr/local/lib/python3.10/site-packages/flask_appbuilder/views.py
RUN sed -i 's/int(pk)/str(pk)/g' /usr/local/lib/python3.10/site-packages/flask_appbuilder/security/manager.py

COPY ./fbc.cfg /fbc.cfg
COPY ./uwsgi.ini /app/uwsgi.ini
COPY ./app /app/app

ENV STATIC_PATH /usr/local/lib/python3.10/site-packages/flask_appbuilder/static
ENV FBC_SETTINGS=/fbc.cfg
ENV LISTEN_PORT=20000
EXPOSE 20000


