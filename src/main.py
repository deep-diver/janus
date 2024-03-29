import os
import json
import argparse
from conversation import gen as conv_gen
from instruct import gen as inst_gen
from utils import get_setup_and_mermaid, push_to_hf_hub

def main(args):
    print(args)
    
    # parse
    print("1. grasp setup")
    setup, mermaid = get_setup_and_mermaid(args.target_folder)
    print("1. grasp setup ...done")
            
    if args.type == "conversation":
        # seeds gen
        print("2. generate seeds")
        seeds = conv_gen.gen_seeds(
            setup, mermaid, args.backend_llm, args.api_key, 
            conv_gen.default_initial_prompt_constructor, args.retry_num
        )
        print("2. generate seeds ...done")

        # derivational gen
        print("3. generate derivations")
        outputs = conv_gen.gen_derivations(
            setup, mermaid, seeds, args.backend_llm, args.api_key, 
            conv_gen.default_derivational_prompt_constructor, 
            args.type, args.retry_num, args.d_factor
        )
        print("3. generate derivations ...done")

    elif args.type == "instruct":
        # seeds gen
        print("2. generate seeds")
        seeds = inst_gen.gen_seeds(
            setup, mermaid, args.backend_llm, args.api_key, 
            inst_gen.default_initial_prompt_constructor, 
            args.retry_num, args.s_factor
        )
        print("2. generate seeds ...done")

        # derivational gen
        print("3. generate derivations")
        outputs = inst_gen.gen_derivations(
            setup, mermaid, seeds, args.backend_llm, args.api_key, 
            inst_gen.default_derivational_prompt_constructor, 
            args.type, args.retry_num, args.d_factor
        )
        print("3. generate derivations ...done")

    # save
    print("4. export")
    file_path = os.path.join(args.target_folder, args.target_filename)
    with open(file_path, 'w') as f:
        json.dump(outputs, f, indent=2)
    print("4. export ...done")
    
    # optional
    if args.hf_hub_repo_id is not None and \
        args.hf_token is not None:
        print("5. export to Hugging Face Hub")
        push_to_hf_hub(file_path, args.hf_hub_repo_id, args.hf_token, args.hf_append)
        print("5. export to Hugging Face Hub ...done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend-llm', default="gemini", choices=["gemini", "gpt"])
    parser.add_argument('--api-key', type=str, required=True, metavar="➡️ API key for backend LLM")
    parser.add_argument('--target-folder', type=str, required=True, metavar="➡️ In which folder to look up for setup.yaml and diagram.mermaid")
    parser.add_argument('--target-filename', type=str, default="outputs.json", metavar="➡️ Filename to store the generated outputs. The file will be created in the same folder as target-folder")
    parser.add_argument('--type', default="conversation", choices=['conversation', 'instruct'], metavar="➡️ Multi-turn conversations or single turn instruction & response")
    parser.add_argument('--s-factor', type=int, default=4, metavar="➡️ How many times to generate outputs on a single direction in seed generation")
    parser.add_argument('--d-factor', type=int, default=4, metavar="➡️ How many times to generate outputs on a single direction in derivational generation")
    parser.add_argument('--retry-num', type=int, default=4, metavar="➡️ How many times to retry when failing at calling Gemini API or parsing JSON")
    
    # Hugging Face Hub (Dataset)
    parser.add_argument('--hf-hub-repo-id', type=str, default=None, metavar="➡️ Repository ID of Hugging Face Hub (Dataset)")
    parser.add_argument('--hf-token', type=str, default=None, metavar="➡️ Hugging Face Hub Access Token")
    parser.add_argument('--hf-append', action='store_true', help="➡️ Whether to append outputs to existing data on the Hugging Face Hub")

    args = parser.parse_args()
    main(args)
