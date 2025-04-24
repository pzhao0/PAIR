import argparse
import sys
import streamlit as st
from conversers import load_guard_and_target_models
from conversers import parse_llama_guard, remove_tokens, get_retry_prompt

NAME = "Evan"

# Function to initialize models
def initialize_models(args):
    guardLM, targetLM = load_guard_and_target_models(args)
    return guardLM, targetLM

# Function to handle chatbot interaction
def chat_with_bot(prompt, guard, guardLM, targetLM):
    target_response = ""  # Ensure target_response is initialized
    
    # If guard is enabled, use the guard model to check for safety
    if guard:
        safe, category = parse_llama_guard(guardLM.query(prompt))
        # print(f"Guard response: {safe}, Category: {category}")
        if safe or category is None:
            target_response = targetLM.query(prompt)
        else:
            retry_prompt = get_retry_prompt(prompt, category)
            target_response = targetLM.query(retry_prompt)
    else:
        # If no guard, just query the target model directly
        target_response = targetLM.query(prompt)

    # Remove unwanted tokens from the response
    return remove_tokens(target_response)

# Streamlit UI setup
def main():
    # Streamlit UI setup
    st.title(f'Chatbot with {NAME}')
    
    # Parse command-line arguments before starting the app
    parser = argparse.ArgumentParser()

    ########### Target model parameters ##########
    parser.add_argument(
        "--target-model",
        default = "gpt-3.5-turbo-1106",
        help = "Name of target model.",
        choices=["vicuna-13b-v1.5", "llama-2-7b-chat-hf", "gpt-3.5-turbo-1106", "gpt-4-0125-preview", "claude-instant-1.2", "claude-2.1", "gemini-pro", "llama2", "llama2-uncensored", "tinyllama", "gemma:2b", "gemma:7b"]
    )
    parser.add_argument(
        "--target-max-n-tokens",
        type = int,
        default = 150,
        help = "Maximum number of generated tokens for the target."
    )
    parser.add_argument(
        "--not-jailbreakbench",
        action = 'store_true',
        help = "Choose to not use JailbreakBench for the target model. Uses JailbreakBench as default. Not recommended."
    )

    parser.add_argument(
        "--jailbreakbench-phase",
        default = "dev",
        help = "Phase for JailbreakBench. Use dev for development, test for final jailbreaking.",
        choices=["dev", "test", "eval"]
    )
    
    ########### Solution parameters #########
    parser.add_argument(
        "--guard",
        action = 'store_true',
        help = "Use the LlamaGuard to evaluate the conversation."
    )
    ##########################################

    # Read arguments passed to the script
    args = parser.parse_args()
    args.use_jailbreakbench = not args.not_jailbreakbench
    
    # Run the Streamlit UI with the parsed arguments
    guardLM, targetLM = initialize_models(args)
    
    # Initialize session state for conversation history
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    # Guard mode toggle using a checkbox
    guard = st.checkbox('Enable LlamaGuard', value=args.guard)

    # Show conversation history
    for sender, message in st.session_state.conversation:
        st.markdown(f"**{sender}:** {message}")
    
    # Handle user input
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""  # Initialize the input if it doesn't exist

    user_input = st.text_input("You:", st.session_state.user_input, key="input_field")

    target_response = ""  # Initialize here to avoid UnboundLocalError
    
    if user_input:
        # Process the user's message
        target_response = chat_with_bot(user_input, guard, guardLM, targetLM)
        
        # Store user input and response in session state
        st.session_state.conversation.append(("You", user_input))
        st.session_state.conversation.append((NAME, target_response))
        
        # Update the session state to keep track of the user's input
        st.session_state.user_input = ""  # Clear input field for next message

    # Display the bot's response
    if target_response:
        st.markdown(f"**{NAME}:** {target_response}")

    # Exit button
    if st.button('Exit'):
        st.session_state.conversation = []  # Clear the conversation history
        st.experimental_rerun()

if __name__ == "__main__":
    main()
