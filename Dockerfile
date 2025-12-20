FROM odoo:18.0

USER root

COPY requirements.txt .

RUN apt-get install -y requirements.txt

USER odoo