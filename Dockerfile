FROM alpine:latest

# Installer curl
RUN apk add --no-cache curl

# Télécharger Prometheus manuellement et le lancer
RUN wget https://github.com/prometheus/prometheus/releases/download/v2.54.1/prometheus-2.54.1.linux-amd64.tar.gz && \
    tar -xzf prometheus-2.54.1.linux-amd64.tar.gz && \
    mv prometheus-2.54.1.linux-amd64 /prometheus && \
    rm prometheus-2.54.1.linux-amd64.tar.gz

WORKDIR /prometheus
CMD ["/prometheus/prometheus", "--config.file=/prometheus/prometheus.yml"]
