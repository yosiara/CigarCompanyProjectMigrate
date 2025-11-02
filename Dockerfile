FROM odoo:18.0

USER root

COPY requirements.txt .

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y requirements.txt

USER odoo