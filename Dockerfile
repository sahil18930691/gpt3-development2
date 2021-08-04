FROM python:3.8

RUN useradd -m SQRYRDS

ENV PYTHONUNBUFFERED 0

ADD requirements.txt /home/SQRYRDS

WORKDIR /home/SQRYRDS

RUN pip install --upgrade pip && \
    pip install --trusted-host pypi.python.org -r requirements.txt && \
    python -m spacy download en_core_web_sm

ADD . /home/SQRYRDS

USER SQRYRDS

EXPOSE 8080

ENV PORT="${PORT:-8080}"

CMD gunicorn main:app --bind 0.0.0.0:$PORT --workers=2 --threads 4 --timeout 60 -k uvicorn.workers.UvicornWorker
