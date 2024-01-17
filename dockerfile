FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /opt/cloudflare-ddns

COPY components ./components

COPY main.py ./

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "./main.py"]