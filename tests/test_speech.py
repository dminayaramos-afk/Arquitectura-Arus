from speech import SpeechRecognizer

r = SpeechRecognizer()

texto = r.transcribe_file("tmp/test.wav")

print("Texto:", texto)
assert isinstance(texto, str)
