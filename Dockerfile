FROM python:3.7
WORKDIR amazons

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python setup.py develop

ENTRYPOINT ["gunicorn", "wsgi:app", "--worker-class", "eventlet" ,"--bind", "0.0.0.0:8000", "--reload"]
CMD ["-w", "1"]
