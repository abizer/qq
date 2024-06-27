qq - command line explainer/generator

notice: doesn't completely work yet, but soon, maybe. printing out colors is not
working correctly

You have a command:

```sh
ffmpeg -i IMG_8011.MOV -vcodec libx264 -crf 23 -preset fast -acodec aac -b:a 128k output.mov
```

but you've forgotten what it means.

```sh
$ qq !!
ffmpeg -i IMG_8011.MOV - Specify the input file IMG_8011.MOV
-vcodec libx264 - Use the libx264 video codec for encoding
-crf 23 - Set the Constant Rate Factor (CRF) value to 23, which determines the quality of the encoded video (lower values mean higher quality)
-preset fast - Use the "fast" preset for the x264 encoder, which trades encoding speed for compression efficiency
-acodec aac - Use the AAC audio codec for encoding
-b:a 128k - Set the audio bitrate to 128 kbps
output.mov - Specify the output file name as output.mov

This command uses FFmpeg to transcode the input video file IMG_8011.MOV to a new file output.mov. It encodes the video using the H.264 codec (libx264) with a CRF value of 23 and the "fast" preset for faster encoding. The audio is encoded using the AAC codec with a bitrate of 128 kbps.
```

Alternatively, you want to generate some command via natural language:

```sh
$ qq -g ffmpeg command to make an mp3 out of the audio of video_file.mp4
ffmpeg -i video_file.mp4 -vn -ar 44100 -ac 2 -b:a 192k -f mp3 audio_file.mp3

This command:

1. `-i video_file.mp4` specifies the input video file.
2. `-vn` tells ffmpeg to remove the video stream and only process the audio.
3. `-ar 44100` sets the audio sampling rate to 44.1kHz (CD quality).
4. `-ac 2` sets the number of audio channels to 2 (stereo).
5. `-b:a 192k` sets the bitrate of the audio to 192kbps (good quality for MP3).
6. `-f mp3` specifies the output format as MP3.
7. `audio_file.mp3` is the name of the output MP3 audio file.

This will extract the audio from the video_file.mp4 and encode it as a stereo MP3 file with a bitrate of 192kbps, suitable for most purposes.
exec (x) / edit (e) / reprompt (r):
```
