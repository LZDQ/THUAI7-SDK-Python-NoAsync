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

# FROM python:3.8-slim

FROM hacker_base

# FROM ubuntu:latest

WORKDIR /app

# ENV BASE_ADDR=

# ENV BASE_PORT=

COPY . .

ENV SAIBLO=1

# RUN apt update && apt clean && apt install -y tcpdump net-tools netcat-openbsd dsniff

# RUN pip install --disable-pip-version-check --break-system-packages -r requirements.txt

ENTRYPOINT ["python", "main.py"]
