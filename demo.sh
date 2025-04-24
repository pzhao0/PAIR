#!/bin/bash

# models=("gpt-3.5-turbo-1106" "tinyllama" "llama2" "llama2-uncensored" "gemma:2b" "gemma:7b")

GUARD="true"
TARGET_MODEL="llama2-uncensored" # choose from model list

streamlit run demo.py -- --guard --target-model "$TARGET_MODEL"