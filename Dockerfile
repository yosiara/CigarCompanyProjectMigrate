FROM odoo:18

USER root

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
    # Requirements \
    && rm -rf /var/lib/apt/lists/*

USER odoo