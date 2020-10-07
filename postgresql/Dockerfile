FROM postgres:9.6-alpine
MAINTAINER Aschwin

# Allow connections; we don't map out any ports so only linked docker containers can connect
RUN echo "host all  all    0.0.0.0/0  md5" >> /var/lib/postgresql/data/pg_hba.conf

# Customize default user/pass/db
ENV POSTGRES_DB amazons
ENV POSTGRES_USER amazons
ENV POSTGRES_HOST_AUTH_METHOD trust

# Include extra setup scripts
ADD docker-entrypoint-initdb.d /docker-entrypoint-initdb.d
