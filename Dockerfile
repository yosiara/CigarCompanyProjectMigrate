FROM odoo:18.0

USER root

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y python3-debugpy

USER odoo