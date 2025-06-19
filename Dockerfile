FROM odoo:18.0

USER root

#odoo_cigarros:18.0
RUN apt-get update && \
    apt-get install -y python3-debugpy

#odoo:17.3 tomando como base 17.1
#RUN python3 -m pip install --upgrade XlsxWriter

#odoo:17.3 tomando como base 17.3
#RUN python3 -m pip install --upgrade jingtrang
# RUN python3 -m pip install --upgrade debugpy pymssql mysql.connector pymysql

#odoo:17.2
#COPY ./entrypoint.sh /
#RUN chown odoo /entrypoint.sh

USER odoo

#odoo:17.2
# ENTRYPOINT ["/entrypoint.sh"]
# CMD ["--update=all --dev=all"]
