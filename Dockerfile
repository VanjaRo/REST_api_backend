FROM python:3.7

RUN mkdir -p /app
WORKDIR /app

COPY . .
RUN apt update -y && apt upgrade -y
RUN apt install -y python3-pip
RUN pip3 install -r /app/requirements.txt

EXPOSE 8080

CMD ["flask", "db", "init", "&&", "flask", "db", "migrate", "&&", "flask", "db", "migrate", "&&", "python3", "main.py"]