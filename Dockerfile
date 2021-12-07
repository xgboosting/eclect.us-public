FROM ubuntu:latest
FROM python:latest
FROM nginx:latest

RUN apt-get update && apt-get install -y \
    software-properties-common
RUN apt-get install -y python3-pip
ADD . /
RUN pip3 install -r daily-be/requirements.txt
#ENV SITE_URL http://localhost:3000
WORKDIR /daily-be
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
