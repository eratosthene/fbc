FROM python:3.10-alpine

RUN apk add --virtual .build-dependencies \
            --no-cache \
            build-base \
            linux-headers \
            git

RUN python -m pip install --upgrade pip gunicorn
COPY ./requirements.txt /app/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN sed -i 's/int(pk)/str(pk)/g' /usr/local/lib/python3.10/site-packages/flask_appbuilder/views.py
RUN sed -i 's/int(pk)/str(pk)/g' /usr/local/lib/python3.10/site-packages/flask_appbuilder/security/manager.py

RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

COPY ./main.py /app/main.py
COPY ./app /app/app

ENV STATIC_PATH=/usr/local/lib/python3.10/site-packages/flask_appbuilder/static
ENV LOG_LEVEL=info

WORKDIR /app
CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:20000", "main:app" ]
EXPOSE 20000
