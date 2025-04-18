ARG PYTHON_VERSION=3.12

FROM bitnami/python:${PYTHON_VERSION}
RUN apt update && apt upgrade -y \
  && apt install curl -y \
  && rm -rf /var/lib/apt/lists/*

# Ensure root certificates are always updated at evey container build
# and curl is using the latest version of them
RUN mkdir /usr/local/share/ca-certificates/cacert.org
RUN cd /usr/local/share/ca-certificates/cacert.org && curl -k -O https://www.cacert.org/certs/root.crt
RUN cd /usr/local/share/ca-certificates/cacert.org && curl -k -O https://www.cacert.org/certs/class3.crt
RUN update-ca-certificates
ENV CURL_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

RUN python -m pip install -U pip
RUN python -m pip install uvicorn

COPY runtimes/ /tmp/runtimes
RUN python -m pip install /tmp/runtimes --no-cache-dir --upgrade
RUN rm -rf /tmp/runtimes

ENV HOST 0.0.0.0
ENV PORT 80
CMD uvicorn titiler_md_demo.main:app --host ${HOST} --port ${PORT}
