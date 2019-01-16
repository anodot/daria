FROM streamsets/datacollector

ARG SDC_LIBS
RUN "${SDC_DIST}/bin/streamsets" stagelibs -install="${SDC_LIBS}"

USER root
RUN apk add --update --no-cache openssh openssh-client openssl
RUN echo "127.0.0.1 daria-test2" >> /etc/hosts

COPY keys/k8s-staging.pem k8s-staging.pem
#RUN chmod 600 k8s-staging.pem && ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -v -i k8s-staging.pem -N -L 80:10.0.0.28:80 ubuntu@100.26.197.230 &