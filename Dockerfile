FROM odoo:17.1

USER root

#base->odoo:17.0
#RUN python3 -m pip install --upgrade debugpy pymssql mysql.connector pymysql

#base->odoo:17.1
COPY ./entrypoint.sh /
RUN chown odoo /entrypoint.sh

USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--update=all --dev=all"]
