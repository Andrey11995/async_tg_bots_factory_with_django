FROM python:3.10-alpine

RUN apk add --no-cache ffmpeg

WORKDIR /app

COPY ./docker/bots/requirements.txt ./requirements/requirements.txt

RUN pip install -r requirements/requirements.txt

RUN rm -rf ./requirements

COPY ./bots ./bots

COPY ./bots/bots_init.py .

RUN rm ./bots/bots_init.py

CMD ["python", "bots_init.py"]
