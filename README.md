# ⛲️ Auto Data Fountain

The goal of Auto Data Fountain is to generate synthetic datasets in order to fine-tune a large language model for arbitrary situations in a systematic way.

## Usage

1. define your own setup in `setup.yaml` and `diagram.mermaid` in a directory. The `setup.yaml` defines basic information such as system prompt, roles of a user and an assistant while `diagram.mermaid` focuses on the entities and their relationship. 

Below shows an example structure of the `setup.yaml` for a basic marriage counsel.
```yaml
initial_prompt: |
  ....

derivational_prompt: |
  ....

output_format: | 
  The generated conversations are recorded in a valid JSON as
  {"conversations":[{"user": text, "assistant": text},...]}.  

delimiter: "------------------------------"

user_role: COUNSELEE
assistant_role: COUNSELOR

seed_evolving_directions:
  - general

derivational_evolving_directions:
  - general
  - in-depth
```

Now, lets have a look into the `diagram.mermaid` for the situation. Note that you can specify much detailed attributes of each entity, and you can also give extra description of the relationship in comments. If you wish to understand of the meaning of it, read this document in raw format since comments are invisible in graphic mode.
```mermaid
erDiagram
    COUNSELOR ||--|{ COUNSELEE : "provides counseling to"

    %% Comments for relationship attributes
    %% Start date: 2024-02-14
    %% Frequency: Weekly
    %% Topic: marriage guidance
```

2. run the following CLI
```bash
$ pip install -r requirements.txt
$ python src/main.py \ 
--gemini-api-key "..." \ 
--target-folder samples/marriage_counsel
```