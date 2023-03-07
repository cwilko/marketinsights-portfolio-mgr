FROM arm64v8/python:3.8-slim-bullseye as target-arm64

FROM arm32v7/python:3.7-slim-buster as target-armv7

FROM target-$TARGETARCH$TARGETVARIANT

ENV PYTHONUNBUFFERED=1

RUN mkdir -p /usr/app
COPY . /usr/app
WORKDIR /usr/app

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends libatlas3-base git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -U --extra-index-url https://www.piwheels.org/simple -r requirements.txt

CMD ["python", "-u", "app.py"]