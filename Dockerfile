FROM python:3.11.3-slim-buster as base

ENV SOURCE_FOLDER  /auto-booker

WORKDIR ${SOURCE_FOLDER}

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