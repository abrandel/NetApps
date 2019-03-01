from watson_developer_cloud import TextToSpeechV1
import os
import Server_keys

def watson_speech(answer):
	text_to_speech = TextToSpeechV1(
		iam_apikey=key1,
		url=url1
	)

	speech_text = str(answer)
	
	with open('answer.mp3', 'wb') as audio_file:
		audio_file.write(
			text_to_speech.synthesize(
				speech_text,
				'audio/mp3',
				'en-US_AllisonVoice'
			).get_result().content)
			
	# TODO: Play the audio file here with OS command
	os.system("omxplayer answer.mp3")
	
	# return to the server 
	return
