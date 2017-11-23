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
RUN pip3 install -r /app/webapp/requirements.txt
WORKDIR /app/webapp/
EXPOSE 8080
CMD python3 app.py
