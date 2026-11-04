ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}
RUN apt update && apt upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ENV CURL_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

RUN python -m pip install -U pip
RUN python -m pip install uvicorn

COPY runtimes/ /tmp/runtimes
RUN python -m pip install /tmp/runtimes --no-cache-dir --upgrade
RUN rm -rf /tmp/runtimes

RUN groupadd -g 1000 user && \
    useradd -u 1000 -g user -s /bin/bash -m user

USER user

ENV HOST 0.0.0.0
ENV PORT 80

CMD uvicorn titiler_md_demo.main:app --host ${HOST} --port ${PORT}
