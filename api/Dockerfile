FROM python:3.10-slim-buster

WORKDIR /app
RUN apt-get update && apt-get install -y gcc python3-dev libpq-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
