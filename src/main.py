import os
import json
import argparse
from conversation.parser import get_setup_and_mermaid
from conversation.gen import gen_seeds, gen_derivations

def main(args):
    if args.type == "conversation":
        # parse
        print("1. grasp setup")
        setup, mermaid = get_setup_and_mermaid(args.target_folder)

        # seeds gen
        print("2. generate seeds")
        seeds = gen_seeds(
            setup, mermaid, args.gemini_api_key, args.retry_num
        )

        # derivational gen
        print("3. generate derivations")
        outputs = gen_derivations(
            setup, mermaid, seeds, args.gemini_api_key, args.retry_num, args.d_factor
        )

        # save
        print("4. export")
        file_path = os.path.join(args.target_folder, args.target_filename)
        with open(file_path, 'w') as f:
            json.dump(outputs, f, indent=4)         
    else:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--gemini-api-key', type=str, required=True)
    parser.add_argument('--target-folder', type=str, required=True)
    parser.add_argument('--target-filename', type=str, default="outputs.json")
    parser.add_argument('--type', type=str, default="conversation")
    parser.add_argument('--d-factor', type=int, default=4)
    parser.add_argument('--retry-num', type=int, default=4)

    args = parser.parse_args()
    main(args)