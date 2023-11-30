FROM spymovil/commsv3_imagen_base:latest

WORKDIR /anep_api
COPY *.py ./
COPY entrypoint.sh .
RUN chmod 777 /anep_api/*
ENTRYPOINT ["sh", "entrypoint.sh"]

EXPOSE 5022


