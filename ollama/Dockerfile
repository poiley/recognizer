FROM ollama/ollama:latest
RUN mkdir -p /root/.ollama
EXPOSE 11434
VOLUME ["/root/.ollama"]
ENTRYPOINT ["/bin/sh", "-c", "ollama serve & sleep 5 && ollama pull $OLLAMA_MODEL && wait"]
