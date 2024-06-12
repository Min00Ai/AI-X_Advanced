import cv2
import numpy as np
import json
import difflib
import pytesseract
from transformers import pipeline  #STT
import os
from moviepy.editor import VideoFileClip, AudioFileClip

# Tesseract OCR 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def detect_significant_change(current_frame, prev_frame, threshold=50000):
    diff = cv2.absdiff(current_frame, prev_frame)
    change_score = np.sum(diff)
    return change_score > threshold

def enhanced_ocr(frame):
    config = ('-l A2+kor+eng --oem 3 --psm 6 -c preserve_interword_spaces=1')
    text = pytesseract.image_to_string(frame, config=config)
    return text

def text_similarity(text1, text2):
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def save_results(detected_texts, output_file='extracted_data.json'):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(detected_texts, file, indent=4, ensure_ascii=False)

def extract_code_from_video_enhanced(video_path, frame_sampling_rate=100, similarity_threshold=0.23):
    cap = cv2.VideoCapture(video_path)
    detected_texts = []
    prev_frame = None
    frame_count = 0
    current_text = ""
    start_time = None  

    # Prepare transformers model for speech recognition
    model = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h")
    audio_path = video_path.replace('.mp4', '.mp3')
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration
    audio_segment_duration = frame_sampling_rate / cap.get(cv2.CAP_PROP_FPS)
    
    # Transcribe the audio
    result = model(audio_path)
    transcriptions = result["text"]

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_sampling_rate == 0:
            if prev_frame is not None:         
                if detect_significant_change(frame, prev_frame, 50000):
                    text = enhanced_ocr(frame)
                    if text.strip() != "":
                        if current_text and text_similarity(text, current_text) < similarity_threshold:
                            end_time = frame_count / cap.get(cv2.CAP_PROP_FPS)
                            related_speech_texts = extract_speech_texts(transcriptions, start_time, end_time, audio_duration)
                            detected_texts.append({
                                "code_start_timestamp": start_time,
                                "code_end_timestamp": end_time,
                                "code_text": current_text,
                                "related_speech_texts": related_speech_texts
                            })
                            current_text = text
                            start_time = frame_count / cap.get(cv2.CAP_PROP_FPS)
                        elif not current_text:
                            current_text = text
                            start_time = frame_count / cap.get(cv2.CAP_PROP_FPS)
                prev_frame = frame  
            else:
                prev_frame = frame
        frame_count += 1

    if current_text:
        end_time = frame_count / cap.get(cv2.CAP_PROP_FPS)
        related_speech_texts = extract_speech_texts(transcriptions, start_time, end_time, audio_duration)
        detected_texts.append({
            "code_start_timestamp": start_time,
            "code_end_timestamp": end_time,
            "code_text": current_text,
            "related_speech_texts": related_speech_texts
        })

    cap.release()
    save_results(detected_texts, 'refined_extracted_data.json')

def extract_speech_texts(transcriptions, start_time, end_time, audio_duration):
    related_speech_texts = []
    start_index = int((start_time / audio_duration) * len(transcriptions))
    end_index = int((end_time / audio_duration) * len(transcriptions))
    related_speech_texts = transcriptions[start_index:end_index]
    return related_speech_texts

# 실행 예시
video_path = './assets/test_video2.mp4'
extract_code_from_video_enhanced(video_path)