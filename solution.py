import argparse
from conversers import load_guard_and_target_models, load_target_model
from conversers import parse_llama_guard, remove_tokens, get_retry_prompt

NAME = "Evan"
targetLM = None

def change_target_model(args, name):
    choices=["gpt-3.5-turbo-1106", "llama2", "llama2-uncensored", "tinyllama", "gemma:2b", "gemma:7b"]
    if name in choices:
        global targetLM
        targetLM = load_target_model(args, name)

def main(args):

    guardLM, targetLM = load_guard_and_target_models(args)
    guard = args.guard
    
    print(f'======= Conversation with {NAME} starting =======')
    print(f'Target model: {targetLM.model_name}')
    print(f'Protections on: {args.guard}')
    print('===============================================')

    prompt = input(">>> ")
    while prompt != "/exit":
        
        if prompt == "/guard":
            guard = True
            print("Protections are now on.")
        elif prompt == "/no-guard":
            guard = False
            print("Protections are now disabled.")
        else:
            target_response = ""
            
            if guard:
                safe, category = parse_llama_guard(guardLM.query(prompt))
                if safe or category is None:
                    target_response = targetLM.query(prompt)
                    safe, category = parse_llama_guard(target_response)
                    if not safe or category is not None:
                        retry_prompt = get_retry_prompt(prompt, category)
                        target_response = targetLM.query(retry_prompt)
                else:
                    retry_prompt = get_retry_prompt(prompt, category)
                    target_response = targetLM.query(retry_prompt)
            else:
                target_response = targetLM.query(prompt)
            
            target_response = remove_tokens(target_response)
            print(f'{target_response}')
            
        prompt = input(">>> ")
        
    print(f'======= Exiting Conversation with {NAME} ========')
    

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    ########### Target model parameters ##########
    parser.add_argument(
        "--target-model",
        default = "gpt-3.5-turbo-1106", #TODO changed
        help = "Name of target model.",
        choices=["gpt-3.5-turbo-1106", "llama2", "llama2-uncensored", "tinyllama", "gemma:2b", "gemma:7b"]
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
        choices=["dev","test","eval"]
    )
    ##################################################
    
    ########### Solution parameters #########
    
    parser.add_argument(
        "--guard",
        action = 'store_true',
        help = "Use the LlamaGuard to evaluate the conversation."
    )
    
    ###############################################
    
    args = parser.parse_args()

    args.use_jailbreakbench = not args.not_jailbreakbench
    main(args)
