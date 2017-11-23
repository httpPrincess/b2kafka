FROM ubuntu:latest
MAINTAINER jj
RUN DBEIAN_FRONTEND=noninteractive apt-get update && \
   apt-get install python3 python3-pip -y && \
   apt-get clean autoclean && \
   apt-get autoremove && \
   rm -rf /var/lib/{apt,dpkg,cache,log}
RUN mkdir /app/
VOLUME /data/
ADD . /app/
RUN pip3 install -r /app/requirements.txt
WORKDIR /data/
CMD sleep 10 && python3 /app/uploader.py
