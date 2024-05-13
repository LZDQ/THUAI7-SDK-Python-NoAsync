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

FROM python:3.10.13-alpine

WORKDIR /app

COPY . .

ENV SAIBLO=1

# COPY site-pkg /usr/local/lib/python3.10/site-packages

RUN pip install --disable-pip-version-check -r requirements.txt

ENTRYPOINT ["python", "main.py"]
