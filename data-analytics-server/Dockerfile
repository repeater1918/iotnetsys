FROM python:3.11.1-slim-buster

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . .

EXPOSE 8000

CMD [ "python3", "-m" , "uvicorn", "aas:app", "--host=0.0.0.0", "--port=8000", "--reload"]