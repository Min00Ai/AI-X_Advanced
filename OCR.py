
import flet as ft
import asyncio
import subprocess
import json
import cv2
import pytesseract
import numpy as np
import difflib
from quiz_generator import Quizgen
from analysis_Code import Analysis_Code
from retreiver import getrtv

# Tesseract OCR 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class VideoOCR:
    def __init__(self, url):
        self.url = url
        self.detected_texts = []  # 인식 텍스트 저장
        self.videoOCRIndex = int(0)

    #  url 동영상 프레임,fps 가져오는 비동기함수
    async def get_video_resolution(self, index):
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate',
            '-of', 'json',
            self.url[index]
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

    # ocr 하는 함수

    def enhanced_ocr(self, frame):
        config = ('-l eng --oem 3 --psm 3 -c preserve_interword_spaces=1')
        text = pytesseract.image_to_string(frame, config=config)
        # print(text)
        return text

    def save_results(self, detected_texts, output_file):
        with open('./scipt_data/' + 'video' + str(output_file) + '.json', 'w', encoding='UTF-8') as file:
            json.dump(detected_texts, file, indent=4, ensure_ascii=False)

    # 비동기식 ocr 수행 함수
    async def process_video(self, index, frame_sampling_rate=10, similarity_threshold=0.23):
        # 여기 오디오와 같이할려면
        width, height, fps = await self.get_video_resolution(int(index))  # 동영상 정보 가져오기
        ffmpeg_command = [
            'ffmpeg',
            '-i', self.url[index],
            '-loglevel', 'quiet',
            '-an',
            '-f', 'image2pipe',
            '-pix_fmt', 'bgr24',
            '-vcodec', 'rawvideo',
            '-'
        ]
        pipe = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, bufsize=10 ** 8)  ## ffmpeg 실행
        frame_size = width * height * 3

        prev_frame = None
        frame_count = 0
        current_text = ""
        start_time = None

        while True:
            raw_frame = pipe.stdout.read(frame_size)
            if not raw_frame:
                break
            frame = np.frombuffer(raw_frame, dtype='uint8').reshape((height, width, 3))

            if frame_count % frame_sampling_rate == 0 and prev_frame is not None:
                if self.detect_significant_change(frame, prev_frame, 50000):
                    text = self.enhanced_ocr(frame)

                    if text.strip() and (not current_text or difflib.SequenceMatcher(None, text,
                                                                                     current_text).ratio() < similarity_threshold):
                        if current_text:
                            self.detected_texts.append({
                                "code_start_timestamp": start_time,
                                "code_end_timestamp": frame_count / fps,
                                "code_text": current_text
                            })
                        current_text = text
                        start_time = frame_count / fps
                prev_frame = frame
            else:
                prev_frame = frame
            frame_count += 1

        if current_text:
            self.detected_texts.append({
                "code_start_timestamp": start_time,
                "code_end_timestamp": frame_count / fps,
                "code_text": current_text
            })
        # json 저장
        self.save_results(self.detected_texts, index)
        self.detected_texts = []

        pipe.terminate()

    # 프레임간 유의미 차이 감지함수
    def detect_significant_change(self, current_frame, prev_frame, threshold=50000):
        diff = cv2.absdiff(current_frame, prev_frame)
        return np.sum(diff) > threshold

    async def process_ocr(self):
        await self.process_video(0)
        await self.process_video(1)
        await self.process_video(2)
        print("OCR끝")


class OCRVideoPlayer:
    def __init__(self, page: ft.Page, urls):
        self.page = page
        self.urls = urls
        self.current_video_index = 0
        self.video_player = None
        self.video_playlist = None
        self.button_container = None
        self.ocr_results = None
        self.setup_ui(0)
        self.quiz = '초기 문제'
        self.ac_result = {"문제": "",
                          "분석 결과": "",
                          "권장 알고리즘": ""}
        self.quizGen = Quizgen()
        self.ac = Analysis_Code()
        self.data=''

    def setup_ui(self, inital_index):
        self.current_video_index = inital_index
        self.playlist = [ft.VideoMedia(url) for url in self.urls]
        self.page.window_width = 1500
        self.video_player = ft.Video(
            expand=6,
            autoplay=False,
            playlist=self.playlist,
            width=700,
            height=500,
            muted=True,

        )
        # 수정

        # 재생목록 설정
        self.playlist_container = ft.Container(
            content=ft.Column([
                ft.TextField(value="정렬 알고리즘", text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton(text="탐색 알고리즘", width=250, on_click=lambda e, i=int(0): self.change_video(i)),
                ft.ElevatedButton(text="부호화", width=250, on_click=lambda e, i=int(1): self.change_video(i)),
                ft.ElevatedButton(text="암호화", width=250, on_click=lambda e, i=int(2): self.change_video(i)),
                ft.ElevatedButton(text="자료 구조", width=250, on_click=lambda e, i=int(3): self.change_video(i)),
                ft.ElevatedButton(text="조건문", width=250, on_click=lambda e, i=int(4): self.change_video(i)),
                ft.ElevatedButton(text="재귀함수", width=250, on_click=lambda e, i=int(5): self.change_video(i)),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            width=600,
            bgcolor=ft.colors.GREY_100,
            # height=500,
            #expand=3
        )
        # 버튼 컨트롤러
        self.button_container = ft.Container(
            content=ft.Row([
                # ft.ElevatedButton(text="Previous", on_click=lambda e: self.video_player.previous()),
                ft.ElevatedButton(text="스크립트", on_click=lambda e: self.update_ui(self.current_video_index)),
                # ft.ElevatedButton(text="Next", on_click=lambda e: self.video_player.next()),
            ], alignment=ft.MainAxisAlignment.CENTER),
            # width=700,
            # margin=5,
            expand=1
        )

        self.video_button_container = ft.Container(
            content=ft.Row([
                ft.ElevatedButton(text="Previous", on_click=self.previous_video),
                ft.ElevatedButton(text="Next", on_click=self.next_video),
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=700,
        )
        self.side_bar_container = ft.Container(
            content=ft.Column([
                ft.CupertinoButton(
                    content=ft.Text("재생목록", color=ft.colors.BLUE),
                    opacity_on_click=0.5,
                    on_click=self.show_playlist),
                ft.CupertinoButton(
                    content=ft.Text("스크립트", color=ft.colors.BLUE),
                    opacity_on_click=0.5,
                    on_click=self.show_script),
                ft.CupertinoButton(
                    content=ft.Text("문제풀이", color=ft.colors.BLUE),
                    opacity_on_click=0.5,
                    on_click=self.show_quiz),
                ft.CupertinoButton(
                    content=ft.Text("메모장", color=ft.colors.BLUE),
                    opacity_on_click=0.5,
                    on_click=self.show_playlist),
                ft.CupertinoButton(
                    content=ft.Text("Q&A", color=ft.colors.BLUE),
                    opacity_on_click=0.5,
                    on_click=self.show_playlist),
            ], alignment=ft.MainAxisAlignment.CENTER, ), expand=1)

        self.ocr_results = ft.ListView(expand=9)

        # OCR 스크립트
        self.script_Container = ft.Container(
            content=self.ocr_results,
            expand=9,
            border_radius=ft.border_radius.all(10)
        )

        # 스크립트와 버튼을 포함한 컨테이너
        self.script_playlist = ft.Container(
            content=ft.Column([
                self.button_container,
                self.script_Container
            ]),
            bgcolor=ft.colors.GREY_100,
            width=600,

        )
        self.user_code_input = ft.TextField(label="코드 입력 하세요", multiline=True, height=400,
                                            suffix=ft.ElevatedButton("답안 제출 하기", on_click=self.analCode))
        # self.analyze_output = ft.text('분석결과',height=400)

        # 문제 생성 문제 해결 스크립트
        self.quiz_container = ft.Container(
            content=ft.Column([
                ft.Text('초기 문제 ', height=400),
                self.user_code_input
            ]), width=600,
        )
        # 비디오 + 이전 이후 버튼
        self.video_container = ft.Container(
            content=ft.Column([
                self.video_player,  # 비디오
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(text="Previous", on_click=self.previous_video),
                        ft.ElevatedButton(text="Next", on_click=self.next_video),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    width=700,
                    margin=10  # 버튼과 비디오 사이의 여백
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            expand=7
            # 비디오 컨테이너의 확장을 늘려서 비디오가 더 커지게
        )

        # 전체
        self.video_playlist = ft.Row([
            self.video_container,
            self.script_playlist,
            self.side_bar_container

        ], alignment=ft.MainAxisAlignment.START, expand=True)

        self.page.add(self.video_playlist)

    def previous_video(self, e):
        if self.current_video_index > 0:
            self.current_video_index -= 1
            self.change_video(self.current_video_index)

    def next_video(self, e):
        if self.current_video_index < len(self.urls) - 1:
            self.current_video_index += 1
            self.change_video(self.current_video_index)

    def show_playlist(self, e):
        self.video_playlist.controls[1] = self.playlist_container
        self.page.update()

    def show_script(self, e):
        self.video_playlist.controls[1] = self.script_playlist
        self.page.update()

    async def show_quiz(self, e):
        self.new_quiz = await self.quizGen.getQuiz()
        print(type(self.new_quiz))
        self.quiz_container = ft.Container(
            content=ft.Column([
                ft.Text(self.new_quiz, height=400),
                self.user_code_input
            ]), width=600,
        )
        self.video_playlist.controls[1] = self.quiz_container
        self.page.update()

    async def analCode(self, e):
        print("analcode눌림")
        self.userCode = self.user_code_input.value
        gptanswer = await self.getac(self.user_code_input.value)

        lines = gptanswer.split('\n')

        # 각 줄의 시작 부분에 있는 불필요한 공백을 제거
        processed_lines = [line.lstrip() for line in lines]

        # 다시 문자열로 결합
        processed_value = ''.join(processed_lines)
        # 중괄호로 감싸기
        json_text = '{' + processed_value + '}'
        print(json_text)
        A_code_json = json.loads(json_text)
        self.ac_result = A_code_json

        gptanswer_content = [
            ft.Text(f"{key}: {value}", selectable=True)
            for key, value in A_code_json.items()
        ]

        print(self.user_code_input.value)

        self.quiz_container = ft.Container(
            content=ft.Column([ \
                ft.Text("분석결과",text_align= ft.alignment.center ,style = ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE | ft.TextDecoration.OVERLINE,size=20)),
                ft.Column(gptanswer_content,),
                ft.Text("사용자코드", text_align=ft.TextAlign.CENTER,
                        style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE | ft.TextDecoration.OVERLINE,size=20)),
                ft.Text(str(self.user_code_input.value)),
                ft.Container(
                    content=ft.ElevatedButton('피드백', on_click=self.go_feedback),
                    alignment=ft.alignment.center
                ),
            ], spacing=10,
            ) ,width=600,
        )
        self.video_playlist.controls[1] = self.quiz_container
        self.page.update()

    def go_feedback(self,e):
        code_start_time, code_end_time, code_topic = 0, 0, 0
        print(self.ac_result['권장 알고리즘'])
        if self.ac_result['권장 알고리즘'] != '0':
            if "삽입 정렬" in self.ac_result['권장 알고리즘']:
                code_start_time, code_end_time, code_topic = getrtv("삽입 정렬 (Insertion Sorting)- 파이썬 구현")
            elif "선택 정렬" in self.ac_result['권장 알고리즘']:
                code_start_time, code_end_time, code_topic = getrtv("선택 정렬 (Selection Sorting) - 파이썬 구현")
            elif "퀵 정렬" in self.ac_result['권장 알고리즘']:
                code_start_time, code_end_time, code_topic = getrtv("퀵 정렬 (Quick Sorting) - 파이썬 구현")
            elif "계수 정렬" in self.ac_result['권장 알고리즘']:
                code_start_time, code_end_time, code_topic = getrtv("계수 정렬 - 파이썬 구현")
            fb_json = {"code_start_timestamp": code_start_time, "code_end_timestamp": code_end_time,
                       "topic": code_topic}
            self.jump_to_ocr_time(e,fb_json['code_start_timestamp'])
        else:
            print("그냥 움직여봐")
            self.jump_to_ocr_time(e, 386.666)

    # def go_feedback(self,e):
    #     code_start_time, code_end_time, code_topic = 0, 0, 0
    #     print(self.ac_result['권장 알고리즘'])
    #     if self.ac_result['권장 알고리즘'] != '0':
    #         if "삽입 정렬" in self.ac_result['권장 알고리즘']:
    #             for item in self.data:
    #                 if item["topic"]=="삽입 정렬 (Insertion Sorting)- 파이썬 구현":
    #                     self.jump_to_ocr_time(e,item["code_start_timestamp"])
    #
    #         elif "선택 정렬" in self.ac_result['권장 알고리즘']:
    #             for item in self.data:
    #                 if item["topic"]=="선택 정렬 (Selection Sorting) - 파이썬 구현":
    #                     self.jump_to_ocr_time(e,item["code_start_timestamp"])
    #         elif self.ac_result["권장 알고리즘"]=="퀵 정렬":
    #             for item in self.data:
    #                 if item["topic"]=="퀵 정렬 (Quick Sorting) - 파이썬 구현":
    #                     self.jump_to_ocr_time(e, item["code_start_timestamp"])
    #         elif "계수 정렬" in self.ac_result['권장 알고리즘']:
    #             for item in self.data:
    #                 if item["topic"]=="계수 정렬 - 파이썬 구현":
    #                     self.jump_to_ocr_time(e, item["code_start_timestamp"])
    #     else:
    #         print("그냥 움직여봐")


    def getQu(self):
        return self.quizGen.getQ()

    async def getac(self, user_code):
        quiz = self.getQu()
        return await self.ac.run(quiz=quiz, user_code=user_code)

    # 동영상 변경함수 , ocr동작 포함
    def change_video(self, video_index):
        self.video_player.jump_to(video_index)
        self.current_video_index = int(video_index)
        self.ocr_results.controls.clear()
        self.page.update()

    # 비디오 인덱스 바꿈
    def set_video_index(self, index):
        self.current_video_index = index
        self.change_video(index)

    # 퀴즈 가져오기
    async def quizGet(self, e):
        quiz = await self.quizGen.getQuiz()
        print(quiz)
        return quiz

    def update_ui(self, index):
        path = './script_data/extracted_data.json'
        print(path)
        with open(path, 'r', encoding='UTF-8') as file:
            self.data = json.load(file)
        self.ocr_results.controls.clear()
        for item in self.data:
            ocr_text_field = ft.TextField(
                value=item["topic"],
                # value=str(n),
                multiline=True,
                width=300,
                height=70,
                bgcolor=ft.colors.BLUE_200
            )

            go_button = ft.ElevatedButton(
                '　',
                icon=ft.icons.SEND_ROUNDED,
                icon_color=ft.colors.PINK_400,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=1)),
                on_click=lambda e, t=item["code_start_timestamp"]: self.jump_to_ocr_time(e, t),
                width=50,
                height=70,
                bgcolor=ft.colors.WHITE
            )
            row = ft.Row([
                ocr_text_field,
                go_button],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0

            )
            self.ocr_results.controls.append(row)
        self.page.update()

    # 텍스트에서 ocr 인식 시작지점으로 이동함수
    def jump_to_ocr_time(self, e, start_time):
        gotime = start_time * 1000
        self.video_player.seek(int(gotime))

        # 비디오 끝 이벤트 처리기


def main(page: ft.Page):
    urls = [
        "https://github.com/SMU-AI-X-Advanced/video/raw/master/assets/dongbinna_sorting_algo.mp4",
        "https://github.com/SMU-AI-X-Advanced/multi-channel-video-analyze/raw/main/only_code.mp4",
        "https://github.com/SMU-AI-X-Advanced/video/raw/master/ocr_audio.mp4",
    ]
    ocr = OCRVideoPlayer(page, urls)  ####


if __name__ == "__main__":
    ft.app(main)
