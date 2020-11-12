FROM python:3.7

LABEL maintainer="mpilo.khathwane@gmail.com"

ENV SERVICE_TTL 300
ENV TZ=Africa/Johannesburg

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./requirements.txt /usr/local/auth-service/
WORKDIR /usr/local/auth-service
RUN pip install -r requirements.txt

COPY  . /usr/local/auth-service
RUN pip install --no-cache-dir -e .

EXPOSE 8575
CMD uwsgi --ini-paste-logged /usr/local/auth-service/auth_service/configuration/development.ini
