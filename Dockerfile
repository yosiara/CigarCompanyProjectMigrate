FROM odoo:18.0

USER root

#odoo_cigarros:18.0
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3-debugpy

USER odoo