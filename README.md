qq - command line explainer/generator

You have a command:

```sh
ffmpeg -i IMG_8011.MOV -vcodec libx264 -crf 23 -preset fast -acodec aac -b:a 128k output.mov
```

but you've forgotten what it means.

```sh
$ qq !!
ffmpeg - A multimedia framework for handling video, audio, and other multimedia files and streams
    -i IMG_8011.MOV - Input file, specified as 'IMG_8011.MOV'
    -vcodec libx264 - Use the H.264 video codec for encoding
    -crf 23 - Set the Constant Rate Factor (CRF) to 23, balancing quality and file size (lower values mean higher quality)
    -preset fast - Use the 'fast' preset for encoding speed (trade-off between compression efficiency and encoding speed)
    -acodec aac - Use the AAC audio codec for encoding
    -b:a 128k - Set the audio bitrate to 128 kbps
    output.mov - Output file, specified as 'output.mov'
This command converts the input video 'IMG_8011.MOV' to 'output.mov' using H.264 for video and AAC for audio, with specified quality and speed settings.
Cost $0.0138
```

Alternatively, you want to generate some command via natural language:

```sh
$ qq -g ffmpeg command to make an mp3 out of the audio of video_file mp4
Command to execute: ffmpeg -i video_file.mp4 -vn -ar 44100 -ac 2 -b:a 192k output_audio.mp3
(e)xplain / e(x)ec / ed(i)t / (r)eprompt / (q)uit > Cost $0.0048
e
ffmpeg - A versatile multimedia processing tool
    -i video_file.mp4 - Input file, in this case, a video file named video_file.mp4
    -vn - Disable video recording (extract audio only)
    -ar 44100 - Set the audio sampling rate to 44100 Hz
    -ac 2 - Set the number of audio channels to 2 (stereo)
    -b:a 192k - Set the audio bitrate to 192 kbps
    output_audio.mp3 - Output file, in this case, an audio file named output_audio.mp3
This command extracts the audio from video_file.mp4, setting the sample rate to 44100 Hz, using stereo channels, and encoding it at 192 kbps, saving the result as output_audio.mp3.
Command to execute: ffmpeg -i video_file.mp4 -vn -ar 44100 -ac 2 -b:a 192k output_audio.mp3
(e)xplain / e(x)ec / ed(i)t / (r)eprompt / (q)uit > Cost $0.0175
r
> input should be movie.mp4 and output song.mp3
Command to execute: ffmpeg -i video_file.mp4 -vn -ar 44100 -ac 2 -b:a 192k output_audio.mp3
Command to execute: ffmpeg -i movie.mp4 -vn -ar 44100 -ac 2 -b:a 192k song.mp3
(e)xplain / e(x)ec / ed(i)t / (r)eprompt / (q)uit > Cost $0.0226
x
ffmpeg version 7.0.1 Copyright (c) 2000-2024 the FFmpeg developers
  built with Apple clang version 15.0.0 (clang-1500.3.9.4)
  ...
```

dependencies: litellm (for now)

installation: `pipx install git+https://github.com/abizer/qq.git`
