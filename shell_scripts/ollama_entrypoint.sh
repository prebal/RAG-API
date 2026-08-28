#!/bin/bash

set -e

ollama serve & 
OLLAMA_PID=$!

echo "Waiting for ollamad to initialize..."
while ! ollama list >/dev/null 2>&1; do
	sleep 1
done

MODEL="${MODEL_NAME:llama3.2:1b}"

if ! ollama list | grep -q "$MODEL"; then
	echo "Model $MODEL not found, downloading it now"
	ollama pull "$MODEL"
else
	echo "Found $MODEL, already present model will be used"
fi 

wait $OLLAMA_PID
