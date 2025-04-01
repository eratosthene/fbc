FROM ghcr.io/multi-py/python-gunicorn:py3.10-alpine-22.0.0

RUN apk add --virtual .build-dependencies \
            --no-cache \
            build-base \
            linux-headers \
            git

RUN python -m pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN sed -i 's/int(pk)/str(pk)/g' /usr/local/lib/python3.10/site-packages/flask_appbuilder/views.py
RUN sed -i 's/int(pk)/str(pk)/g' /usr/local/lib/python3.10/site-packages/flask_appbuilder/security/manager.py

RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

COPY ./main.py /app/main.py
COPY ./app app

ENV STATIC_PATH=/usr/local/lib/python3.10/site-packages/flask_appbuilder/static
ENV FLASK_RUN_PORT=20000
ENV PORT=20000
ENV WORKERS=8

