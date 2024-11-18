FROM odoo:17.1

USER root

#odoo:17.1
#RUN python3 -m pip install --upgrade debugpy pymssql mysql.connector pymysql

#odoo:17.3 tomando como base 17.1
RUN python3 -m pip install --upgrade XlsxWriter

#odoo:17.2
#COPY ./entrypoint.sh /
#RUN chown odoo /entrypoint.sh

USER odoo

#odoo:17.2
# ENTRYPOINT ["/entrypoint.sh"]
# CMD ["--update=all --dev=all"]
