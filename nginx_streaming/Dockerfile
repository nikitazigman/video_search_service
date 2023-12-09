FROM ubuntu:20.04

ENV GIT_SSL_NO_VERIFY=1

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    git \
    libpcre3 \
    libpcre3-dev \
    libssl-dev \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/streaming-server

RUN git clone https://github.com/arut/nginx-rtmp-module.git \
    && git clone https://github.com/nginx/nginx.git \
    && cd nginx \
    && ./auto/configure --add-module=../nginx-rtmp-module \
    && make \
    && make install

COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./entrypoint.sh ./entrypoint.sh
COPY ./tmp/hls /tmp/hls

ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]
