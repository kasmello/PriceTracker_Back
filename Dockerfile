FROM python:3.11
WORKDIR /script
COPY requirements.txt /script/
RUN pip install -r requirements.txt
COPY . /script
CMD python connectToNeo4J.py