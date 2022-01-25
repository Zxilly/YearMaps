FROM python:3-slim

WORKDIR /app

EXPOSE 5000/tcp

RUN pip install yearmaps

CMD yearmaps-server

