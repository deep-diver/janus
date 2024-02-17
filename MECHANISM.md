# MECHANISM

This additional document describe how Janus works under the hood. 

## PREREQUSITES

Before using Janus, please make sure you have a folder with `setup.yaml` and `diagram.mermaid` files inside. `setup.yaml` could be structured in many different ways, but it is recommended to following the below structure if you want to use Janus CLI. If you modify the source code, or if you want to use Janus as API, then you can define your own structure. Below is an example from `samples/coding_assist/setup.yaml`

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