FROM python:3.10-alpine

RUN apk add --virtual .build-dependencies \
            --no-cache \
            python3-dev \
            build-base \
            linux-headers \
            pcre-dev

RUN apk add --no-cache pcre uwsgi-python3 python3

WORKDIR /app
COPY ./uwsgi.ini /app
COPY ./requirements.txt /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN sed -i 's/int(pk)/str(pk)/g' /usr/local/lib/python3.10/site-packages/flask_appbuilder/views.py
RUN sed -i 's/int(pk)/str(pk)/g' /usr/local/lib/python3.10/site-packages/flask_appbuilder/security/manager.py

RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

COPY ./app /app

ENV STATIC_PATH /usr/local/lib/python3.10/site-packages/flask_appbuilder/static

EXPOSE 5000
CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]

