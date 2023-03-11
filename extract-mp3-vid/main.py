import moviepy
import moviepy.editor

video = moviepy.editor.VideoFileClip("") # Path to video .mp4
audio = video.audio
audio.write_audiofile('exported.mp3')