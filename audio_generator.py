from google.cloud import texttospeech
from flask import make_response

# Instantiates a client
client = texttospeech.TextToSpeechClient()

def generate_audio(text):
  # Set the text input to be synthesized
  synthesis_input = texttospeech.SynthesisInput(text=text)

  # Build the voice request, select the language code ("en-US") and the ssml
  # voice gender ("neutral")
  voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
  )

  # Select the type of audio file you want returned
  audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
  )

  # Perform the text-to-speech request on the text input with the selected
  # voice parameters and audio file type
  response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
  )


  audio_response = make_response(response.audio_content)
  audio_response.headers['Content-Type'] = 'audio/wav'
  audio_response.headers['Content-Disposition'] = 'attachment; filename=sound.wav'
  return audio_response
