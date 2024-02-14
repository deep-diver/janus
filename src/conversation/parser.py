import os
import yaml

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