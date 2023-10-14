from pyRTMP import RTMP
import cv2
import pyaudio
import numpy as np
import time
import logging
import random
import string


rtmp_url = "rtmp://localhost"


stream_key = "stream_" + time.strftime("%Y%m%d_%H%M%S") + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


rtmp = RTMP(rtmp_url)

audio_format = pyaudio.paInt16
audio_channels = 1
audio_sample_rate = 44100
audio_chunk = 1024
audio = pyaudio.PyAudio()
audio_stream = audio.open(
    format=audio_format,
    channels=audio_channels,
    rate=audio_sample_rate,
    input=True,
    frames_per_buffer=audio_chunk
)

video_width = 1280  
video_height = 720  
frame_rate = 30    
cap = cv2.VideoCapture(0)  
cap.set(3, video_width)   # Set the initial width
cap.set(4, video_height)  # Set the initial height
cap.set(5, frame_rate)    # Set the frame rate


font = cv2.FONT_HERSHEY_SIMPLEX
font_color = (0, 255, 0)
font_thickness = 2


log_filename = "stream_log.txt"
logging.basicConfig(filename=log_filename, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


max_retries = 3
retry_count = 0


start_time = time.time()


stream_status = "Connecting..."

def capture_and_stream_video():
    global retry_count, video_width, video_height, frame_rate, stream_status
    while retry_count < max_retries:
        try:

            rtmp.connect()

            rtmp.publish(stream_key)

            while True:
                ret, frame = cap.read()
                if not ret:
                    break


                elapsed_time = int(time.time() - start_time)
                fps = round(1 / (time.time() - start_time), 2)
                overlay_text = f"FPS: {fps} | Time Elapsed: {elapsed_time} sec | Status: {stream_status}"
                cv2.putText(frame, overlay_text, (10, 30), font, 1, font_color, font_thickness)


                rtmp.write_video(encoded_frame)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            retry_count += 1
            if retry_count < max_retries:
                logging.error(f"Retrying (attempt {retry_count} of {max_retries})...")
                stream_status = "Reconnecting..."

                time.sleep(5) 
            else:
                logging.error("Max retry count reached. Exiting.")
                stream_status = "Max retries reached. Stream stopped."

        finally:
            
            rtmp.close()

def capture_and_stream_audio():
    while retry_count < max_retries:
        try:
            while True:
                
                audio_data = audio_stream.read(audio_chunk)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)

                
                rtmp.write_audio(audio_array.tobytes())

        except Exception as e:
            logging.error(f"An error occurred in audio stream: {e}")
            retry_count += 1
            if retry_count < max_retries:
                logging.error(f"Retrying audio stream (attempt {retry_count} of {max_retries})...")
                
                time.sleep(5)  
            else:
                logging.error("Max retry count reached for audio stream. Exiting.")

        finally:
            
            audio_stream.stop_stream()
            audio_stream.close()
            audio.terminate()


video_thread = threading.Thread(target=capture_and_stream_video)
audio_thread = threading.Thread(target=capture_and_stream_audio)

video_thread.start()
audio_thread.start()


video_thread.join()
audio_thread.join()


cap.release()
