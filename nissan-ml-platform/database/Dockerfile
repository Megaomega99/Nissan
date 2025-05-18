# database/Dockerfile
FROM postgres:15

# Copiar script de inicialización
COPY init.sql /docker-entrypoint-initdb.d/

# Configurar variables de entorno
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=nissan_ml

# Exponer puerto
EXPOSE 5432