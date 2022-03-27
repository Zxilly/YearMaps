FROM python:3-slim

WORKDIR /app

EXPOSE 5000/tcp

COPY dist/yearmaps*.whl /app

ENV TZ="Asia/Shanghai" \
    DEBIAN_FRONTEND=noninteractive

RUN fl=$(ls /app | grep "yearmaps.*\.whl") && \
    apt-get update && \
    apt install -y fonts-noto-cjk tzdata && \
    ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo ${TZ} > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/* && \
    pip install $fl && \
    rm -rf $fl

CMD yearmaps-server

