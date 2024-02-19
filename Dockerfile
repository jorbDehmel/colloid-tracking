FROM python:3

ARG DOCKER_USER=default_user

RUN apt update && apt upgrade -y && apt install -y git

RUN adduser ${DOCKER_USER}
USER $DOCKER_USER

RUN pip install pandas numpy matplotlib

CMD bash

# Launch this w/ a given data path
# DATA_PATH=/home/jorb/data && docker run --rm --mount type=bind,source=${DATA_PATH},target=/extern/data -i -t janus:latest
