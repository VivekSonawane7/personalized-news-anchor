from a4f_local import A4F

client = A4F()

try:
    audio_bytes = client.audio.speech.create(
        model="tts-1",  # Model name (currently informational)
        input="Hello! my name is Vivek Sonawane",
        voice="sage"   # Choose a supported voice
    )
    with open("output.mp3", "wb") as f:
        f.write(audio_bytes)
    print("Generated output.mp3")
except Exception as e:
    print(f"An error occurred: {e}")