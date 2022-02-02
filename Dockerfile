FROM python:3-slim

WORKDIR /app

EXPOSE 5000/tcp

COPY dist/yearmaps*.whl /app/yearmaps.whl

RUN apt-get update && \
    apt install -y fonts-noto-cjk && \
    rm -rf /var/lib/apt/lists/*
RUN pip install yearmaps.whl && \
    rm -rf /app/yearmaps.whl

CMD yearmaps-server

