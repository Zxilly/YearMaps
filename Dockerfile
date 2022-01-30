FROM python:3-slim

WORKDIR /app

EXPOSE 5000/tcp

RUN apt-get update && \
    apt install -y fonts-noto-cjk && \
    rm -rf /var/lib/apt/lists/*
RUN pip install yearmaps==0.0.15

CMD yearmaps-server

