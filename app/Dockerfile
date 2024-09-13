FROM python:3.10-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# COPY Pipfile Pipfile.lock ./
COPY req.txt .
RUN python -m pip install --upgrade  pip --progress-bar off
# RUN pip install --progress-bar off pipenv && pipenv install --dev  --progress-bar off
RUN pip install -r req.txt --progress-bar off

RUN apt-get update
RUN apt-get install -y wget unzip 
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -P /tmp
RUN apt-get install -y /tmp/google-chrome-stable_current_amd64.deb 
RUN rm /tmp/google-chrome-stable_current_amd64.deb
RUN apt-get clean

WORKDIR /app
COPY . /ap
