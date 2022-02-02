FROM python:3-slim

WORKDIR /app

EXPOSE 5000/tcp

COPY dist/yearmaps*.whl /app

RUN fl=$(ls /app | grep "yearmaps.*\.whl") && \
    apt-get update && \
    apt install -y fonts-noto-cjk && \
    rm -rf /var/lib/apt/lists/* && \
    pip install $fl && \
    rm -rf $fl

CMD yearmaps-server

