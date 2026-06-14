#Languange use to 
FROM python:3.10-slim

WORKDIR /vault-app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

EXPOSE 9000

CMD ["python","-u","app.py"]
