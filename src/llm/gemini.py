import google.generativeai as genai

def determine_model_name(given_image=None):
  if given_image is None:
    return "gemini-1.0-pro"
  else:
    return "gemini-1.0-pro-vision-latest"

def construct_image_part(given_image):
  return {
    "mime_type": "image/jpeg",
    "data": given_image
  }

def call_gemini(prompt="", API_KEY=None, given_text=None, given_image=None, generation_config=None, safety_settings=None):
  genai.configure(api_key=API_KEY)

  if generation_config is None:
    generation_config = {
      "temperature": 0.9,
      "top_p": 1,
      "top_k": 32,
      "max_output_tokens": 8192,
    }

  if safety_settings is None:
    safety_settings = [
      {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
      },
      {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
      },
      {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
      },
      {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
      },
    ]

  model_name = determine_model_name(given_image)
  model = genai.GenerativeModel(model_name=model_name,
                                generation_config=generation_config,
                                safety_settings=safety_settings)

  prompt_parts = [prompt]
  if given_image is not None:
    prompt_parts.append(construct_image_part(given_image))

  response = model.generate_content(prompt_parts)
  return response.text