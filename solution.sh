#!/bin/bash

# models=("gpt-3.5-turbo-1106" "tinyllama" "llama2" "llama2-uncensored" "gemma:2b" "gemma:7b")

GUARD="true"
TARGET_MODEL="llama2" # choose from model list

if [ "$GUARD" == "true" ]; then
    python3 solution.py --target-model "$TARGET_MODEL" --guard
else
    python3 solution.py --target-model "$TARGET_MODEL"
fi