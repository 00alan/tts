### Timeline
##### *Summary of the development journey this repo has taken thus far*
1) ~3hrs set up voice interaction interface, in this case a python script run locally
	- a script that in theory should have been easy to create from gpt prompting was made very difficult due to python interactions with audio hardware devices (and diff os audio software? not sure)
	- abandoned macos development, was able to achieve working version on windows. key breakthrough was in using vosk+pyaudio instead of speech_recognition lib for audio processing
2) ~3hrs attempted and abandoned integration of dialogflow model for response generation (much harder to get off the ground than cheaply available llm api.... for use cases with necessity of precise and highly deterministic answers, will be preferable over gpt models)
3) ~2hrs integrated gpt4o for response generation via openai api, and explored options for integrating select information into gpt4o responses, e.g. calendar availability, navigation instructions
4) ~(in progress) integration of select privately accessed knowledge/info into gpt4o responses

##### v6 is latest working version, v7 in development, other versions have been deleted but can be retrieved from commit history.


#### outputs

Listening...
Processing your question: can i schedule an appointment for february eighth ten a m

Assistant reponse: Sure! To schedule that appointment, could you please provide your name?

Listening...
Processing your question: alan

Assistant reponse: It seems like your message got cut off. How can I assist you with Alan?

Listening...

