FROM python:3.7-alpine

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

# CMD ["python", "data_processor.py"]
CMD ["./wait-for-broker.sh", "python", "data_processor.py"]