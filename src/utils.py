import os
import yaml
import json

def find_json_snippet(raw_snippet):
	json_parsed_string = None

	json_start_index = raw_snippet.find('{')
	json_end_index = raw_snippet.rfind('}')

	if json_start_index >= 0 and json_end_index >= 0:
		json_snippet = raw_snippet[json_start_index:json_end_index+1]
		try:
			json_parsed_string = json.loads(json_snippet, strict=False)
		except:
			raise ValueError('failed to parse string into JSON format')
	else:
		raise ValueError('No JSON code snippet found in string.')

	return json_parsed_string

def parse_first_json_snippet(snippet):
	json_parsed_string = None

	if isinstance(snippet, list):
		for snippet_piece in snippet:
			try:
				json_parsed_string = find_json_snippet(snippet_piece)
				return json_parsed_string
			except:
				pass
	else:
		try:
			json_parsed_string = find_json_snippet(snippet)
		except Exception as e:
			print(e)
			raise ValueError()

	return json_parsed_string

def get_setup_and_mermaid(folder_path):
    mermaid = None
    setup_yaml_path = os.path.join(folder_path, 'setup.yaml')
    mermaid_path = os.path.join(folder_path, 'diagram.mermaid')

    if not os.path.isfile(setup_yaml_path):
        raise FileNotFoundError(f"setup.yaml not found in {folder_path}")

    with open(setup_yaml_path, 'r') as file:
      setup = yaml.safe_load(file)

    if 'er_diagram' in setup:
      mermaid = setup['er_diagram']
    elif 'er_diagram_path' in setup:
      mermaid_path = os.path.join(folder_path, setup['er_diagram_path'])

    if mermaid is None:
      if not os.path.isfile(mermaid_path):
          raise FileNotFoundError(f"diagram.mermaid not found in {folder_path}")

      with open(mermaid_path, 'r') as file:
        mermaid = file.read()

    return setup, mermaid.strip()