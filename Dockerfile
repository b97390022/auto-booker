FROM python:3.11.3-slim-bullseye as base

ENV SOURCE_FOLDER=/auto-booker

WORKDIR ${SOURCE_FOLDER}

RUN apt-get update -y && \
    apt-get install -y wget gnupg unzip

RUN wget -q -O- https://dl.google.com/linux/linux_signing_key.pub | apt-key add -  && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google.list

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y google-chrome-stable libgconf-2-4 libnss3-dev libgdk-pixbuf2.0-dev libgtk-3-dev libxss-dev && \
    rm -rf /var/lib/apt/lists/*

ADD requirements.txt ${SOURCE_FOLDER}

RUN pip install -r requirements.txt

COPY . ${SOURCE_FOLDER}

CMD python -m src.main

#########################
FROM base as test

#layer test tools and assets on top as optional test stage
RUN apt-get update && apt-get install -y curl

#########################
FROM base as final

# this layer gets built by default unless you set target to test