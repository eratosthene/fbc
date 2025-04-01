FROM python:3.10-alpine

RUN apk add --no-cache pkgconf

RUN apk add --virtual .build-dependencies \
            --no-cache \
            build-base \
            linux-headers \
            git

RUN python -m pip install --upgrade pip
RUN python -m pip install uwsgi
COPY ./requirements.txt /app/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN sed -i 's/int(pk)/str(pk)/g' /usr/local/lib/python3.10/site-packages/flask_appbuilder/views.py
RUN sed -i 's/int(pk)/str(pk)/g' /usr/local/lib/python3.10/site-packages/flask_appbuilder/security/manager.py

RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

COPY ./uwsgi.ini /app
COPY ./app /app/app

ENV STATIC_PATH /usr/local/lib/python3.10/site-packages/flask_appbuilder/static
ENV FLASK_RUN_PORT=20000

EXPOSE 20000
CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]

