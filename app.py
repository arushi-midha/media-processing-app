import streamlit as st
import speech_recognition as sr
import moviepy.editor as mp
import os

# Function to convert video to audio
def video_to_audio(video_file, audio_file):
    clip = mp.VideoFileClip(video_file)
    clip.audio.write_audiofile(audio_file)

# Function to transcribe audio to text
def audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    transcription = ""

    with sr.AudioFile(audio_file) as source:
        total_duration = int(source.DURATION)
        offset = 0
        while offset < total_duration:
            chunk_duration = min(60, total_duration - offset)
            chunk = recognizer.record(source, duration=chunk_duration)
            try:
                text = recognizer.recognize_google(chunk)
                transcription += text + " "
            except sr.UnknownValueError:
                transcription += "[Unrecognized Speech] "
            except sr.RequestError:
                transcription += "[API Error] "
            offset += chunk_duration

    return transcription

# Main Streamlit app
def main():
    st.title("Media Processing App")
    st.write("Choose a function:")

    # Buttons for different functionalities
    option = st.radio("Select an option:", ("Audio to Text", "Video to Audio", "Video to Text"))

    if option == "Audio to Text":
        st.subheader("Audio to Text")
        audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])

        if audio_file is not None:
            st.audio(audio_file, format="audio/wav")

            temp_audio_path = "temp_audio.wav"
            with open(temp_audio_path, "wb") as f:
                f.write(audio_file.getbuffer())

            with sr.AudioFile(temp_audio_path) as source:
                st.write("Transcribing the audio...")
                recognizer = sr.Recognizer()
                recognizer.adjust_for_ambient_noise(source)
                audio_text = recognizer.listen(source, phrase_time_limit=30)

            try:
                text = recognizer.recognize_google(audio_text)
                st.write("Transcription:")
                st.text_area("", text, height=200)

                st.download_button("Download Transcription", text, file_name="transcription.txt", mime="text/plain")

            except sr.RequestError:
                st.write("API is unreachable. Check your internet connection.")
            except sr.UnknownValueError:
                st.write("Unable to recognize speech.")
            finally:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)

    elif option == "Video to Audio":
        st.subheader("Video to Audio")
        video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

        if video_file is not None:
            st.video(video_file)

            temp_video_path = "temp_video.mp4"
            temp_audio_path = "output_audio.mp3"
            
            with open(temp_video_path, "wb") as f:
                f.write(video_file.getbuffer())

            if st.button("Extract Audio"):
                video_to_audio(temp_video_path, temp_audio_path)
                st.success("Audio extracted successfully!")

                st.audio(temp_audio_path, format="audio/mp3")

                with open(temp_audio_path, "rb") as f:
                    st.download_button("Download Audio", f, file_name="output_audio.mp3", mime="audio/mpeg")

    elif option == "Video to Text":
        st.subheader("Video to Text")
        video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

        if video_file is not None:
            video_path = os.path.join(video_file.name)
            audio_path = os.path.splitext(video_path)[0] + ".wav"

            with open(video_path, "wb") as f:
                f.write(video_file.getbuffer())

            video_to_audio(video_path, audio_path)
            st.success("Audio extracted from video.")

            with st.spinner("Transcribing audio..."):
                transcription = audio_to_text(audio_path)

            st.success("Audio transcribed to text.")
            st.text_area("Transcribed Text", transcription, height=200)

            st.download_button("Download Transcription", transcription, file_name="transcription.txt", mime="text/plain")

    # Footer section
    footer = """<style>
a:link , a:visited{
color: white;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: lavender;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: grey;
color: white;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤ by <a style='display: block; text-align: center;' href="https://github.com/arushi-midha" target="_blank">Arushi Midha</a></p>
</div>
"""
    st.markdown(footer, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
