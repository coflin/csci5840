FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
	apt-get install -y iputils-ping net-tools curl isc-dhcp-client apache2 vim
