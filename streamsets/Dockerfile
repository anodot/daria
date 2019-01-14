FROM streamsets/datacollector

USER root
RUN apk add --update --no-cache openssh openssh-client openssl
RUN echo "127.0.0.1 daria-test2" >> /etc/hosts

COPY keys/k8s-staging.pem k8s-staging.pem
COPY keys/daria-test2.crt daria-test2.crt