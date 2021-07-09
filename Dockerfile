FROM python:3.6-alpine

RUN adduser -S SQRYDS

ENV PYTHONUNBUFFERED 0

ADD requirements.txt /home/SQRYDS

WORKDIR /home/SQRYDS

RUN pip install --upgrade pip && pip install --trusted-host pypi.python.org -r requirements.txt

ADD . /home/SQRYDS

USER SQRYDS

EXPOSE 8080

ENV PORT="${PORT:-8080}"

CMD gunicorn main:app --bind 0.0.0.0:$PORT -k uvicorn.workers.UvicornWorker
