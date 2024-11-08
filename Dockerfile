FROM odoo:17.0

USER root

# Image odoo:17.0 build
#RUN apt update && \
#    apt install -y git && \
#    apt install nano && \
#    apt install -y python3-mysql.connector && \
#    apt install -y python3-mysqldb && \
#    apt install -y python3-pymssql && \
#    apt install -y python3-pymysql
RUN python3 -m pip install --upgrade debugpy pymssql mysql.connector pymysql
    

# Put odoo modules inside container for production deploy
#RUN mkdir /workspaces
#RUN mkdir /workspaces/CigarCompanyProyectMigrate
#COPY ./ /workspaces/CigarCompanyProyectMigrate

USER odoo
