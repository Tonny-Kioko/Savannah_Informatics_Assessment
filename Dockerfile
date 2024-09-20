# Official base image
FROM python:3.9-slim-buster

# set work directory
WORKDIR /savannah

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY requirements.txt /savannah/

RUN pip install -r requirements.txt

RUN ls -la /savannah/

CMD ["bash", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && python manage.py makemigrations && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
