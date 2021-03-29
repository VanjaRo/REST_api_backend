FROM python:3.7

RUN mkdir -p /app
WORKDIR /app

COPY . .
RUN apt update -y && apt upgrade -y
RUN apt install -y python3-pip
RUN pip3 install -r /app/requirements.txt

RUN chmod +x /app/docker-entrypoint.sh
ENV FLASK_APP main.py

EXPOSE 8080

CMD ["/bin/bash", "docker-entrypoint.sh"]