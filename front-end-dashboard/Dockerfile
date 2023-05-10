FROM python:3.11.1-slim-buster

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . .

EXPOSE 80

CMD ["python3", "-m", "gunicorn", "maindash:server", "--bind", "0.0.0.0:80", "--workers", "2"]