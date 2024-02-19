# MECHANISM

This additional document describe how Janus works under the hood. 

### STEPS

The entire steps are described clearly in the [main.py](https://github.com/deep-diver/janus/blob/main/src/main.py).

```bash
$ python src/main.py \
--backend-llm gemini --api-key "..." \
--target-folder samples/marriage_counsel --type conversation \
--hf-hub-repo-id chansung/test-ds --hf-token "..." --hf-append 
```

0. Prerequisite
    - Janus works based on a target folder, so you need to create a folder (name doesn't matter).
    - inside the folder, there should be `setup.yaml`, and you can optionally have `diagram.mermaid` file.

1. Parsing the setup & diagram
    - look for `setup.yaml` and `diagram.mermaid` files in the folder specified in `--target-folder`.
      - `setup.yaml` is the fixed filename, there should be file named as `setup.yaml`.
      - the content of `diagram.mermaid` could be directly defined inside `setup.yaml`. In this case, define the diagram in `er_diagram` key.
    - parse the `setup.yaml` and `diagram.mermaid` files.

2. Generating seed (prompt, output) pairs
    - concatenate necessary parts from `setup.yaml` in a single string to form a prompt.
      - the default concatenation rule is defined is [default_initial_prompt_constructor](https://github.com/deep-diver/janus/blob/main/src/conversation/gen.py#L7) as `prompt = f"{initial_prompt % (mermaid, delimiter, evolving_direction, user_role, assistant_role)}{output_format}"`. The matching placeholders could be found in the `initial_prompt` field inside the `setup.yaml`.
    - iterate the following process for `len(evolving_directions)` times.
      - evolving_directions is a list defined in the `setup.yaml`.
      - each evolving_direction gives additional information into the prompt how the conversation should be drived.
      - at each time, the prompt generates output in the format defined as in the `output_format` field inside the `setup.yaml`.
      - at each time, the generated output is parsed and stored in a list (basically, each output is a sequence of conversations between user and assistant).
    - the list with the outputs generated from all directions is called **seeds**.

3. Generating derivation (prompt, output) pairs
    - iterate over each seed
      - incrementally split the sub-conversations on a seed (i.e. given `{user: hi, assistant, hello}, {user: nice to meet you, assistant: good to see you}`, at first only `{user: hi, assistant, hello}`, then at second `{user: hi, assistant, hello}, {user: nice to meet you, assistant: good to see you}`)
      - iterate the incrementally splitted sub-conversations
        - iterate each evolving direciton as defined in the `derivational_evolving_directions` inside `setup.yaml`
          - iterate the number of `derivational factor` which is given via the CLI's `--d-factor` option.
          - this allows us to generate diverse converstations on the same situations
            - at each time, the prompt generates output in the format defined as in the `output_format` field inside the `setup.yaml`.
            - at each time, the generated output is parsed and stored in a list (basically, each output is a sequence of conversations between user and assistant).
    - the list with the outputs is returned.

This step basically let partial conversations to be continued in many different directions with multiple diversion.

4. Exporting to a external JSON file
    - the outputs from the step 3 is stored in an external JSON file

5. (Optional) Export to Hugging Face Dataset on the Hub 
    - load up the exported JSON file as `datasets`
    - look for the Hugging Face Dataset repo specified in the CLI's `--hf-hub-repo-id` option
      - if the repo doesn't exist, the repo with the name will be created
      - if the repo exists, and if CLI's `--hf-append` option is specified, load up the existing dataset on the repo as `datasets` 
    - if the CLI's `--hf-append` option is specified, combine the existing dataset with the newly generated dataset
      - if not, just the newly generated dataset. this will overwrite the repo's existing dataset 
    - upload the final results

### `setup.yaml`

`setup.yaml` could be structured in many different ways, but it is recommended to following the below structure if you want to use Janus CLI. If you modify the source code, or if you want to use Janus as API, then you can define your own structure. Below is an example from `samples/coding_assist/setup.yaml`

```yaml
category: coding assist

initial_prompt: |
  %s # erDiagram
  %s # delimiter
  The above erDiagram describes the basic setup of a certain scene.

  Generate possible first few conversations between a user and an assistant based on the erDiagram.
  The conversations should sound natural and logical.
  The direction or the style of the conversations should be "%s". # direction
  The conversations should be occured without exposuring the underlying information of the erDiagram.

  The user should play the role of "%s" appeared in the erDiagram. The user should focus on the given role. # user role
  The assistant should play the role of "%s" appeared in the erDiagram. The assistant should focus on the given role. # assistant role
  Based on the words that the user say, the assistant gives appropriate, detailed, and long answers.

derivational_prompt: |
  %s # erDiagram
  %s # delimiter
  The above erDiagram describes the basic setup of a certain scene.

  Generate possible follow-up conversations between a user and an assistant based on the erDiagram and the first few conversations: %s # first few conversation in JSON str.
  The conversations should sound natural and logical.
  The direction or the style of the conversations should be "%s". # direction
  The conversations should be occured without exposuring the underlying information of the erDiagram.

  The user should play the role of "%s" appeared in the erDiagram. The user should focus on the given role. # user role
  The assistant should play the role of "%s" appeared in the erDiagram. The assistant should focus on the given role. # assistant role
  Based on the words that the user say, the assistant gives appropriate, detailed, and long answers.

output_format: |
  The generated conversations are recorded in a valid JSON as
  {"conversations":[{"user": text, "assistant": text},...]}.

delimiter: "------------------------------"

user_role: JUNIOR_DEVELOPER
assistant_role: SENIOR_DEVELOPR

seed_evolving_directions:
  - general
  - diverse

derivational_evolving_directions:
  - general
  - in-depth
```

Let's go one by one

- `category`: a string to manage the category of generated dataset. this information will be recorded in the output JSON file.

- `initial_prompt`: initial prompt template to generate seed (prompt, output) pairs. The `%s` placeholders are replaced by the actual values from the internal logic. If you use Janus as API, you can define your own replacement logic. Take a look into the [default example](https://github.com/deep-diver/janus/blob/97a4e62d4e80490dec53b16a706cf60e180c67dc/src/conversation/gen.py#L7C5-L7C39). All the relevant information could be injected such as relational diagram(a.k.a erDiagram), the roles of user and assistant, evolving direction, and so on. 
  - if you choose to use Janus as API, the information to be injected is not limited to the ones from the example. Since all the information from the YAML will be parsed and given as an argument, you can define additional information in YAML and utilize it.

- `derivational_prompt`: prompt template to generate more data based on the seeds. This is basically similar to the `initial_prompt`, but information `first few conversation in JSON str` is additionally injected. 

- `output_format`: defines how the output should be formatted. This section shouldn't be changed for now since all the parsing logic is hard coded based on this.

- `user_role` and `assistant_role`: strings to be injected into the `intial_prompt` and `derivational_prompt` to clarify the roles of user and assistant. Someone might ask why not parsing the roles from `diagram.mermaid`. User's role is likely clearly defined in the `diagram.mermaid`, but assistant's role is not. For instance, we just want to describe a situation that a person interacting with objects. In this situation, the object shouldn't be the assistant, rather assistant could be a child psychologist.

- `seed_evolving_directions`: this will drive the `initial_prompt` in many different directions to generate seed (prompt, output) pairs. It is recommended to use keywords that broadly capture the scene such as General, Overview, Broad, Wide-ranging, Sweeping, Expansive, Global, Universal, All-encompassing, Holistic, Diverse, Varied, Eclectic, Multifaceted, Wide-ranging, Divergent, Heterogeneous, Mixed, Assorted, Comprehensive, Alternative, Innovative, Creative, Unique, Unconventional, Original, Non-traditional, Fresh, Novel, Distinctive, Simple, Basic, Fundamental, Straightforward, Uncomplicated, Clear-cut, Elementary, Accessible, Understandable, Easy.

- `derivational_evolving_directions`: this will drive the `derivational_prompt` in many different directions go generate output (prompt, output) pairs. It is recommended to use keywords that drive the seed scenes in specific and complex such as Complex, Intricate, Multilayered, Complicated, Sophisticated, Elaborate, Involved, Detailed, Nuanced, Dense, Specific, Abstract, Analytical, Humorous,Controversial, Personal, Technical, Emotional, Focus, Perspective, Tangent, Depth, Breadth, Specificity, Context.

### `diagram.mermaid`

`diagram.mermaid` basically contains erDiagram based on [Mermaid](https://mermaid.js.org/syntax/entityRelationshipDiagram.html) syntax. However, If you are not familiar with Mermaid yet
  - The official doc comes with straight forward explanation to understand its syntax, and it is not difficult to draw diagrams manually.
  - However, there are various tools around it as well. For instance, the official website comes with [Mermaid Live Editor](https://mermaid.live/), or [Mermaid Flow](https://www.mermaidflow.app/) provides [Visual Editor](https://www.mermaidflow.app/flowchart), or there are VSCode extensions as well.
  - Also, if you are familar with SQL syntax, there are conversion tools such as [sql2mermaid](https://github.com/nkato/sql2mermaid) that turn SQL to Mermaid relational diagram as well.

Since `diagram.mermaid` is just a chunk of text, and since LLM could understand text, you can actually use comments for much detailed description or the relationship between entities. Take the below example

```
erDiagram
    COUNSELOR {
      specialization behavioristic-psychology
    }
    COUNSELEE {
      sex male
      marriage-duration 10-years
    }
    COUNSELOR ||--|{ COUNSELEE : "provides counseling to"

    %% Comments for relationship attributes
    %% Start date: 2024-02-14
    %% Frequency: Weekly
    %% Topic: marriage guidance
```

It doesnt exactly have to follow the Mermaid syntax, but mimicking Mermaid syntax as much as possible could be ideal.
