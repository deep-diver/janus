import json
from tqdm import tqdm
from llm.gemini import call_gemini
from utils import parse_first_json_snippet

def default_initial_prompt_constructor(setup, mermaid, evolving_direction):
    initial_prompt = setup['initial_prompt']
    output_format = setup['output_format']
    delimiter = setup['delimiter']

    user_role = setup['user_role']
    assistant_role = setup['assistant_role']

    prompt = initial_prompt % (mermaid, delimiter, evolving_direction, user_role, assistant_role)
    prompt = f"{prompt}\n{output_format}"
    return prompt

def default_derivational_prompt_constructor(setup, mermaid, base_conversation, evolving_direction):
    derivational_prompt = setup['derivational_prompt']
    output_format = setup['output_format']
    delimiter = setup['delimiter']

    user_role = setup['user_role']
    assistant_role = setup['assistant_role']

    prompt = derivational_prompt % (mermaid, delimiter, json.dumps(base_conversation), evolving_direction, user_role, assistant_role)
    prompt = f"{prompt}\n{output_format}"
    return prompt

def gen_data(prompt, retry_num, gemini_api_key):
    cur_retry = 0
    data_json = None
    data = None

    while (data_json is None or data is None) and \
            cur_retry <= retry_num:

        data_json = None
        data = None

        try:
            data_json = call_gemini(
                prompt=prompt,
                API_KEY=gemini_api_key
            )

            data = parse_first_json_snippet(data_json)
        except:
            cur_retry = cur_retry + 1
            continue

    return data

def gen_seeds(
    setup, mermaid, gemini_api_key, prompt_constructor, retry_num=4
):
    outputs = []
    seed_evolving_directions = setup["seed_evolving_directions"]

    for evolving_direction in tqdm(seed_evolving_directions, desc="seed generation", unit="direction"):
        prompt = prompt_constructor(setup, mermaid, evolving_direction)
        output = gen_data(prompt, retry_num, gemini_api_key)

        if output is not None:
            outputs.append(output)

    return outputs

def gen_derivations(
    setup, mermaid, seed_conversations, gemini_api_key, derivational_prompt_constructor, retry_num=4, d_factor=4
):
    outputs = []
    derivational_evolving_directions = setup["derivational_evolving_directions"]

    for seed_conversation in tqdm(seed_conversations, unit="seed"):
        base_conversation = []

        for conversation in tqdm(seed_conversation['conversations'], unit="conversation"):
            base_conversation.append(conversation)

            for evolving_direction in tqdm(derivational_evolving_directions, unit="direction"):
                prompt = derivational_prompt_constructor(setup, mermaid, base_conversation, evolving_direction)

                for _ in range(d_factor):
                    output = gen_data(prompt, retry_num, gemini_api_key)

                    if output is not None:
                        count = 0
                        for conv in output["conversations"]:
                            if len(conv) != 2:
                                break
                            
                            count = count + 1
                        
                        if count == len(output["conversations"]):
                            outputs.append(output["conversations"])

    return outputs

