FROM python:3.12

WORKDIR /code

COPY ./requirements.txt requirements.txt

RUN apt-get update

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

#CMD ["mlflow ui --host 0.0.0.0"]