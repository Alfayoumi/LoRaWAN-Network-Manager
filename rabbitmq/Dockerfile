FROM rabbitmq:3.11.3-management-alpine

WORKDIR /usr/local/bin/
ADD ./init.sh .
RUN chmod +x ./init.sh

CMD ["./init.sh"]
