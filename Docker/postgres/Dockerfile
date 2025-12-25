FROM postgres:16
COPY ./postgres_entrypoint.sh /docker-entrypoint-initdb.d/postgres_entrypoint.sh
RUN chmod +x /docker-entrypoint-initdb.d/postgres_entrypoint.sh
