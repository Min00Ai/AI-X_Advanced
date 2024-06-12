import difflib
import pytesseract
import numpy as np
import subprocess
import json
import cv2
from transformers import pipeline
from moviepy.editor import VideoFileClip, AudioFileClip

class VideoOCR:
    def __init__(self, urls):
        self.urls = urls
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.model = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h")

    # 영상 fps, 프레임 가져오는 함수
    def get_video_resolution(self, url):
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate',
            '-of', 'json',
            url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception("Failed to get video resolution")
        info = json.loads(result.stdout)
        width = info['streams'][0]['width']
        height = info['streams'][0]['height']
        r_frame_rate = info['streams'][0]['r_frame_rate']
        numerator, denominator = map(int, r_frame_rate.split('/'))
        fps = numerator / denominator if denominator != 0 else 0
        return width, height, fps

    def detect_significant_change(self, current_frame, prev_frame, threshold=50000):
        diff = cv2.absdiff(current_frame, prev_frame)
        return np.sum(diff) > threshold

    def enhanced_ocr(self, frame):
        config = '-l A2+kor+eng --oem 3 --psm 6 -c preserve_interword_spaces=1'
        return pytesseract.image_to_string(frame, config=config)

    def text_similarity(self, text1, text2):
        return difflib.SequenceMatcher(None, text1, text2).ratio()

    def save_results(self, detected_texts, output_file='extracted_data.json'):
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(detected_texts, file, indent=4, ensure_ascii=False)



    def process_video(self, video_index, frame_sampling_rate=100, similarity_threshold=0.23):
        audio_file_name ='hakmuran.mp3'
        ffmpeg_command = [
            'ffmpeg',
            '-i', self.urls[video_index],  # 입력 파일
            '-loglevel', 'quiet',  # 로그 출력 억제
            '-an',  # 비디오 처리 중 오디오 스트림 무시
            '-f', 'image2pipe',  # 비디오 파이프라인 설정
            '-pix_fmt', 'bgr24',  # 픽셀 포맷 설정
            '-vcodec', 'rawvideo',  # 비디오 코덱 설정
            '-',
            '-vn',  # 오디오? 무시
            '-acodec', 'libmp3lame',  # 오디오 코덱 설정
            '-ar', '44100',  # 샘플 레이트 설정
            '-ac', '2',  # 오디오 채널 수 설정
            '-ab', '192k',  # 오디오 비트레이트 설정
            audio_file_name  # 오디오 출력 파일 명  ############## 이걸 조절해서 해야할듯
        ]
        pipe = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        width, height, fps = self.get_video_resolution(self.urls[video_index])
        frame_size = width * height * 3
        detected_texts = []
        prev_frame = None
        frame_count = 0
        current_text = ""
        start_time = None



        while True:
            raw_frame = pipe.stdout.read(frame_size)
            if not raw_frame:

                print("끝")
                break
            frame = np.frombuffer(raw_frame, dtype='uint8').reshape((height, width, 3)) # 프레임 받아오기

            cv2.imshow("video", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if frame_count % frame_sampling_rate == 0 and prev_frame is not None:
                if self.detect_significant_change(frame, prev_frame, 50000):
                    text = self.enhanced_ocr(frame)
                    print(text)
                    if text.strip() and (not current_text or self.text_similarity(text, current_text) < similarity_threshold):
                        if current_text:
                            detected_texts.append({
                                "start_timestamp": start_time,
                                "end_timestamp": frame_count / fps,
                                "text": current_text
                            })
                        current_text = text
                        start_time = frame_count / fps
                prev_frame = frame
            else:
                prev_frame = frame

            frame_count += 1

        if current_text:
            detected_texts.append({
                "start_timestamp": start_time,
                "end_timestamp": frame_count / fps,
                "text": current_text
            })
        stderr_output = pipe.stderr.read()
        print("여기는 왜안옴?")
        detected_texts = self.extract_speech_text(audio_file_name,detected_texts)


        cv2.destroyAllWindows()
        pipe.terminate()
        self.save_results(detected_texts, 'hak_ocr.json')

    def get_audio_duration(self,mp3_path):
        audio = AudioFileClip(mp3_path)
        duration = audio.duration
        audio.close()
        return duration

    def extract_speech_text(self,mp3_path,jsondata): # json 파일 들어와야하고 model도 들어오고
        duration = self.get_audio_duration(mp3_path)
        print("모델전")
        result= self.model(mp3_path)
        print("모델후")
        transcriptions =result["text"]

        for item in jsondata:
            start = item["start_timestamp"]
            end = item['end_timestamp']
            start_index = int((start / duration) * len(transcriptions))
            end_index = int((end / duration) * len(transcriptions))
            item['speech']=transcriptions[start_index:end_index]
        return jsondata

if __name__ == "__main__":
    urls = [
        "https://user-images.githubusercontent.com/28951144/229373720-14d69157-1a56-4a78-a2f4-d7a134d7c3e9.mp4",
        "https://github.com/SMU-AI-X-Advanced/video/raw/master/ocr_audio.mp4",
        "https://github.com/SMU-AI-X-Advanced/multi-channel-video-analyze/raw/main/only_code.mp4"
    ]
    ocr_processor = VideoOCR(urls)
    ocr_processor.process_video(2)

