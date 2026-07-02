FROM mongo:7.0

COPY mongod.conf /etc/mongod.conf

COPY /src/scripts/init-mongo.js /docker-entrypoint-initdb.d/

EXPOSE 27017

USER mongodb

CMD ["mongod", "--config", "/etc/mongod.conf"]
