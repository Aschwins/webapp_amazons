FROM python:3.12

RUN adduser amazons
WORKDIR /home/amazons/
RUN chown -R amazons /home/amazons

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
RUN python setup.py develop

ENV FLASK_APP run.py

COPY script/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
