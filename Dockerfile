FROM python:3.5

EXPOSE 5000

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Install prerequisites
RUN apt-get update && apt-get install -y \
curl

COPY . /app

CMD python run.py
