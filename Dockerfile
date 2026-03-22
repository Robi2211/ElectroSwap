FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "run.py"]
