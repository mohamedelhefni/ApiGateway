FROM kong:alpine

# Install the js-pluginserver
USER root
RUN apk update
RUN apk add  nodejs npm python3  vim nano
RUN npm install kong-pdk -g

