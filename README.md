### Quickstart

#### *.env file*
Not pushed to github. Contains sensitive material such as api keys. 

#### *vosk models*
Not pushed to github due to size - download models locally via https://alphacephei.com/vosk/models and update model_path var accordingly.

### Overview

##### This python repo has been developed on windows os with Dell supported audio drivers.

Run assistant.py to interact. It makes calls to openai api to access their stateless gpt models (such as gpt-4o-mini, which is currently used). Currently the stateless nature of llm usage accessed through api calls is not specific to openai but is also the case with Anthropic, Google Bard, Meta LLaMA and others.

As such, relevant conversation context must be stored in local memory and fed into the api call. The current working version does so by maintaining a queue of the 10 most recent messages and feeding these back in each call.

In order to guide the stateless api model's purpose, we give the model system instructions during each api call in addition to conversation context. A flowchart of the current instruction logic is shown in system_instructions.jpg.
