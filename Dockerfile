FROM python:3.11

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install --upgrade pip

RUN pip install -r requirements.txt



EXPOSE 8080

CMD [python, main.py]
