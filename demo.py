import argparse
import streamlit as st
import sys
from conversers import load_guard_and_target_models, load_target_model
from conversers import parse_llama_guard, remove_tokens, get_retry_prompt

NAME = "Evan"
targetLM = None

def change_target_model(args, name):
    choices = ["gpt-3.5-turbo-1106", "llama2", "llama2-uncensored", "tinyllama", "gemma:2b", "gemma:7b"]
    if name in choices:
        global targetLM
        targetLM = load_target_model(args, name)

def chat_with_bot(prompt, guard, guardLM, targetLM):
    target_response = "" 
    
    if guard:
        safe, category = parse_llama_guard(guardLM.query(prompt))
        if safe or category is None:
            target_response = targetLM.query(prompt)
        else:
            retry_prompt = get_retry_prompt(prompt, category)
            target_response = targetLM.query(retry_prompt)
    else:
        target_response = targetLM.query(prompt)

    return remove_tokens(target_response)


def main():
    
    parser = argparse.ArgumentParser()

    ########### Target model parameters ##########
    parser.add_argument(
        "--target-model",
        default="gpt-3.5-turbo-1106",
        help="Name of target model.",
        choices=["gpt-3.5-turbo-1106", "llama2", "llama2-uncensored", "tinyllama", "gemma:2b", "gemma:7b"]
    )
    
    ########### Solution parameters #########
    parser.add_argument(
        "--guard",
        action='store_true',
        help="Use the LlamaGuard to evaluate the conversation."
    )
    ##########################################

    args = parser.parse_args()
    args.target_max_n_tokens = 150

    guardLM, targetLM = load_guard_and_target_models(args)

    st.title(f'SafeLLM', anchor=None)
    guard = args.guard
    
    with st.expander("Settings", expanded=False):
        guard = st.checkbox('Enable LlamaGuard', value=args.guard)
        
        model_options = ["gpt-3.5-turbo-1106", "llama2", "llama2-uncensored", "tinyllama", "gemma:2b", "gemma:7b"]
        selected_model = st.selectbox('Select Target Model', model_options, index=model_options.index(args.target_model))
        
        change_target_model(args, selected_model)
        
        if st.button('Clear Conversation'):
            st.session_state.messages = []  
            st.rerun()

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
        
    if user_input := st.chat_input("Type your message and hit enter..."):
        
        st.chat_message("user").markdown(user_input)
        
        st.session_state.messages.append({"role": "user", "content": user_input})

        target_response = chat_with_bot(user_input, guard, guardLM, targetLM)

        with st.chat_message("assistant"):
            st.markdown(target_response)
        
        st.session_state.messages.append({"role": "assistant", "content": target_response})

if __name__ == "__main__":
    main()
