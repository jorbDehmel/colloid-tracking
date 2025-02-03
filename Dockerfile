FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y build-essential git ffmpeg python3 \
    python3-pytest python3-pytest-cov python3-numpy \
    python3-pandas mypy flake8 python3-hypothesis
WORKDIR /host
