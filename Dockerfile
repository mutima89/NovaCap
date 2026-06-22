FROM python:3.11-slim

WORKDIR /app

COPY . .

EXPOSE 8080 8081

CMD ["python", "arbitrage_academy.py"]
