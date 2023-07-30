FROM python:3.10

WORKDIR /web

RUN apt-get update && apt-get install -y gettext && apt-get install -y nano

RUN pip install --upgrade pip

COPY ./docker/web/requirements.txt ./requirements/requirements.txt

RUN pip install -r requirements/requirements.txt

RUN rm -rf ./requirements

CMD ["/bin/bash", "./start_server.sh"]
