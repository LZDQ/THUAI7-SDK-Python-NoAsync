# syntax=docker/dockerfile:1

# FROM python:3.11.9-slim-bookworm AS build-env
# WORKDIR /app
# COPY . .
# RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt
#
# FROM gcr.nju.edu.cn/distroless/python3-debian12
# WORKDIR /app
# COPY --from=build-env /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# COPY --from=build-env /app .
# ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
# ENTRYPOINT ["python", "main.py"]

FROM python:3.8-slim

# FROM ubuntu:latest

WORKDIR /app

COPY . .

ENV SAIBLO=1

ENV BASE_ADDR=183.173.243.130

ENV BASE_PORT=8000

# COPY site-pkg /usr/local/lib/python3.10/site-packages

# RUN apt install -y python-is-python3 pip

RUN pip install --disable-pip-version-check --break-system-packages -r requirements.txt

RUN apt update && apt install -y tcpdump net-tools netcat-openbsd dsniff

ENTRYPOINT ["python", "main.py"]
