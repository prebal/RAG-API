FROM ollama/ollama:0.33.0

COPY shell_scripts/ollama_entrypoint.sh /ollama_entrypoint.sh

RUN chmod +x /ollama_entrypoint.sh

ENTRYPOINT ["/ollama_entrypoint.sh"]
