FROM python:3.11-slim

WORKDIR /app

COPY . .

# Listen on all interfaces inside the container; publish ports on 127.0.0.1 only (see README)
ENV NOVACAP_BIND=0.0.0.0

EXPOSE 8080 8081

CMD ["python", "arbitrage_academy.py"]
