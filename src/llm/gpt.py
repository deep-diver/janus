from openai import OpenAI

def determine_model_name(given_image=None):
    if given_image is None:
        return "gpt-4"
    else:
        return "gpt-4-vision-preview"

def construct_image_part(prompt_parts, given_image):
    prompt = prompt_parts[0]["content"]
    prompt_parts[0]["content"] = [
        {
            "type": "text",
            "text": prompt
        },
        {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64, {given_image}",
            # "resize": ...
        }
    ]
    
    return prompt_parts

def call_gpt(prompt="", API_KEY=None, given_text=None, given_image=None, generation_config=None, safety_settings=None):
    client = OpenAI(api_key=API_KEY)
    
    if generation_config is None:
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "max_tokens": 4096,
            "stream": False
        }

    model_name = determine_model_name(given_image)

    prompt_parts = [{"role": "user", "content": prompt}
    ]
    if given_image is not None:
        prompt_parts = construct_image_part(prompt_parts, given_image)

    response = client.chat.completions.create(
        model=model_name,
        messages=prompt_parts,
        **generation_config
    )
    
    return model_name, response.choices[0].message.content