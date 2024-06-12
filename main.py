

import asyncio
import json
from flet import *
from quiz_generator import Quizgen
from analysis_Code import Analysis_Code
from OCR import OCRVideoPlayer, VideoOCR
import flet as ft
from retreiver import getrtv

class uiMain:
    def __init__(self):
        self.quizGen = Quizgen()
        self.ac = Analysis_Code()
        self.urls = [
            "https://github.com/SMU-AI-X-Advanced/video/raw/master/assets/dongbinna_sorting_algo.mp4",
            "https://github.com/SMU-AI-X-Advanced/multi-channel-video-analyze/raw/main/only_code.mp4",
            "https://github.com/SMU-AI-X-Advanced/video/raw/master/ocr_audio.mp4",
        ]
        self.ocr = VideoOCR(self.urls)
        # self.ac_result = {"문제":"",
        #                   "분석 결과":"",
        #                   "권장 알고리즘":""}

    async def main(self, page: Page):
        self.userCode = ''
        page.bgcolor = colors.WHITE
        async def analCode(e):
            page.go("/analCode")
            self.userCode = user_code_input.value
            ac = await getac(user_code_input.value)
            page.update()
            return ac

        page.title = "다해 PYTHON 인강"
        page.window_width = 1500
        image = Image(src="/assets/image/main_page.png", width=400, height=400, fit=ImageFit.COVER)
        # id_TF = TextField(label="아이디를 입력해주세요.",width=100)
        # pw_TF = TextField(label="아이디를 입력해주세요.",width=100)
        pb1 = ft.MenuBar(
            style=ft.MenuStyle(
                bgcolor=ft.colors.WHITE),
            controls=[
                    ft.SubmenuButton(
                        content= Column([Image(src="./assets/image/video.png",width=50,height=50),Text("강의 목록",size=15,)],alignment=MainAxisAlignment.CENTER,tight=True),
                        style= ft.ButtonStyle(bgcolor=colors.WHITE),
                        controls=[
                            ft.MenuItemButton(
                                content = Text("정렬 알고리즘"),
                                on_click =lambda e: sel_lecture(e, 1)
                            ),
                            ft.MenuItemButton(
                                content = Text("탐색 알고리즘"),
                                on_click =lambda e: sel_lecture(e, 2)
                            ),
                            ft.MenuItemButton(
                                content = Text("부호화"),
                                on_click =lambda e: sel_lecture(e, 3)
                            ),
                            ft.MenuItemButton(
                                content = Text("암호화"),
                                on_click =lambda e: sel_lecture(e, 4)
                            ),
                            ft.MenuItemButton(
                                content = Text("자료 구조"),
                                on_click =lambda e: sel_lecture(e, 5)
                            )
                        ]
                    )
                ]
            )
        quiz = ''


        user_code_input = TextField(label="코드 입력 하세요", multiline=True,height=400,
                                    suffix=ElevatedButton("답안 제출 하기", on_click=analCode))

        async def login_btn(e):
            print("버튼눌림")
            page.go("/login")
            page.update()
            #await self.run_ocr_background()  # ocr 없으면 주석 ㄱ


        page.add(
            Container(
                content = Row([
                    Image(src="./assets/image/icon.png", width=200,height=70, fit=ImageFit.FILL),
                    Text("초심자도 쉽게 확실하게 배우자!"),
                    Container(width=0, expand=True),
                    Text("로그인 / 회원가입",size=15)
                    ],
                    alignment=ft.MainAxisAlignment.START,            
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                width=page.window_width,
                bgcolor=colors.WHITE
 
            ),
            Container(
                content= Row([
                    Container(content=Column([Image(src="./assets/image/company.png",width=50,height=50),Text("회사 소개",size=15,)],alignment=MainAxisAlignment.CENTER),border=ft.border.all(0.3, "black"),width= 200,height=100,alignment=ft.alignment.center,bgcolor=colors.WHITE),
                    Container(content=pb1,border=ft.border.all(0.3, "black"),width= 200,height=100,alignment=ft.alignment.center,bgcolor=colors.WHITE),
                    Container(content=Column([Image(src="./assets/image/test.png",width=50,height=50),Text("코딩 테스트",size=15,)],alignment=MainAxisAlignment.CENTER),border=ft.border.all(0.3, "black"),width= 200,height=100,alignment=ft.alignment.center,bgcolor=colors.WHITE),
                    Container(content=Column([Image(src="./assets/image/my_page.png",width=50,height=50),Text("마이 페이지",size=15,)],alignment=MainAxisAlignment.CENTER),border=ft.border.all(0.3, "black"),width= 200,height=100,alignment=ft.alignment.center,bgcolor=colors.WHITE),
                    Container(content=Column([Image(src="./assets/image/counsel.png",width=50,height=50),Text("고객 센터",size=15,)],alignment=MainAxisAlignment.CENTER),border=ft.border.all(0.3, "black"),width= 200,height=100,alignment=ft.alignment.center,bgcolor=colors.WHITE),
                    Container(content=Column([Image(src="./assets/image/qna.png",width=50,height=50),Text("Q & A",size=15,)],alignment=MainAxisAlignment.CENTER),border=ft.border.all(0.3, "black"),width= 200,height=100,alignment=ft.alignment.center,bgcolor=colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0
                ),
            ),
            Container(
                content= Row(
                [   Container(
                    width=200,height=0),
                    Image(src="./assets/image/main_banner.png", width=page.window_width-400,height=400, fit=ImageFit.FILL),
                    Container(width=200,height=0),
            ],
            width=page.window_width,
            height=400,
            ),
            ),
        )

        # async def getAnalCode():
        #     text = self.ac.getAC()
        #     # 줄 단위로 분리
        #     lines = text.split('\n')
        #
        #     # 각 줄의 시작 부분에 있는 불필요한 공백을 제거
        #     processed_lines = [line.lstrip() for line in lines]
        #
        #     # 다시 문자열로 결합
        #     processed_value = ''.join(processed_lines)
        #     # 중괄호로 감싸기
        #     json_text = '{' + processed_value + '}'
        #     print(json_text)
        #     A_code_json = json.loads(json_text)
        #     self.ac_result = A_code_json
        #     return A_code_json
        
        #복습 피드백 부분  끝나는 부분 주석으로 줄 그어둘게 중간에 jump to ocr 함수는 v3에 있어서 아래 함수 v3에서 구현할 것
        
        # def go_feedback(e):
        #     code_start_time, code_end_time, code_topic = 0,0,0
        #     print(self.ac_result['권장 알고리즘'])
        #     if self.ac_result['권장 알고리즘'] != '0':
        #         if "삽입 정렬" in self.ac_result['권장 알고리즘']:
        #             code_start_time, code_end_time, code_topic = getrtv.getrtv("삽입 정렬 (Insertion Sorting)- 파이썬 구현")
        #         elif "선택 정렬" in self.ac_result['권장 알고리즘']:
        #             code_start_time, code_end_time, code_topic =getrtv("선택 정렬 (Selection Sorting) - 파이썬 구현")
        #         elif "퀵 정렬" in self.ac_result['권장 알고리즘']:
        #             code_start_time, code_end_time, code_topic =getrtv("퀵 정렬 (Quick Sorting) - 파이썬 구현")
        #         elif "계수 정렬" in self.ac_result['권장 알고리즘']:
        #             code_start_time, code_end_time, code_topic =getrtv("계수 정렬 - 파이썬 구현")
        #         fb_json={"code_start_timestamp": code_start_time,"code_end_timestamp": code_end_time,"topic":code_topic}
        #         self.jump

        
        # def fb_update_ui(json_data):
        #     ocr_text_field = ft.TextField(
        #                 value=json_data["topic"],
        #                 # value=str(n),
        #                 multiline=True,
        #                 width=400,
        #                 height=70,
        #                 bgcolor=ft.colors.BLUE_200
        #         )
        #     go_button = ft.ElevatedButton(
        #                 '　',
        #                 icon=ft.icons.SEND_ROUNDED,
        #                 icon_color=ft.colors.PINK_400,
        #                 style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=1)),
        #                 on_click=lambda e, t=json_data["code_start_timestamp"]: OCRVideoPlayer.jump_to_ocr_time(e, t),
        #                 width=50,
        #                 height=70,
        #                 bgcolor=ft.colors.WHITE
        #         )
        #     row = ft.Row([
        #             ocr_text_field,
        #             go_button],
        #             alignment=ft.MainAxisAlignment.CENTER,
        #             spacing=0
        #         )
        #     OCRVideoPlayer.ocr_results.controls.append(row)
        #     page.go("/lecture1")
        #     page.update()

                #-----------------------------------------------------------------------------------------------------------

        def check_item_clicked(e):
            e.control.checked = not e.control.checked
            page.update()

        def sel_lecture(e, lecture_num):
            page.go(f"/lecture{lecture_num}")
            page.update()

        async def quizGen(e):
            quiz = await self.quizGen.getQuiz()
            page.go("/quizGen")
            page.update()
            return quiz

        def getQu():
            return self.quizGen.getQ()

        async def getac(user_code):
            quiz = getQu()
            return await self.ac.run(quiz=quiz, user_code=user_code)

        async def route_change(e):
            page.views.clear()
            if page.route == "/login":
                page.views.append(
                    View(
                        "/login",
                        [
                            AppBar(title=Text("파이썬 기초 강의"), bgcolor=colors.SURFACE_VARIANT),
                            Text("쉽고 간편하게 배우자 다해 코딩 과외", style="bodyMedium", size=20),
                            Text("\n\n기초 파이썬 프로그래밍 강의\n기초부터 심화 학습까지"),
                            Row([Text("1주차강의(변수)"), ElevatedButton("1강", on_click=lambda e: sel_lecture(e, 1))]),
                            Row([Text("2주차강의(상수)"), ElevatedButton("2강", on_click=lambda e: sel_lecture(e, 2))]),
                            Row([Text("3주차강의(정렬)"), ElevatedButton("3강", on_click=lambda e: sel_lecture(e, 3))]),
                            Row([Text("4주차강의(함수)"), ElevatedButton("4강", on_click=lambda e: sel_lecture(e, 4))]),
                            Row([Text("5주차강의(객체)"), ElevatedButton("5강", on_click=lambda e: sel_lecture(e, 5))]),
                            Row([Text("6주차강의(조건)"), ElevatedButton("6강", on_click=lambda e: sel_lecture(e, 6))]),
                        ],
                    )
                )

            elif page.route == "/lecture1":
                self.player = OCRVideoPlayer(page, self.urls)
                self.player.setup_ui(inital_index=0)
                page.views.append(
                    View(
                        "/lecture1",
                        [
                            AppBar(
                                title=Text("1강 변수", size=30), bgcolor=colors.SURFACE_VARIANT
                            ),
                            self.player.video_playlist,
                            # ElevatedButton("강의 복습 및 퀴즈 풀기", on_click=quizGen)
                        ],
                    )
                )
                page.update()

            # elif page.route == "/quizGen":
            #     page.views.append(
            #         View(
            #             "/quizGen",
            #             [
            #                 AppBar(title=Text("강의 복습 및 퀴즈 풀기 ", size=30), bgcolor=colors.SURFACE_VARIANT),
            #                 Column(controls=[Text(getQu()),user_code_input],
            #                        scroll=ft.ScrollMode.ALWAYS,
            #                        height=page.height
            #                        )
            #             ],
            #         )
            #     )
            # elif page.route == "/analCode":
            #     page.views.append(
            #         View(
            #             "/analCode",
            #             [
            #                 AppBar(title=Text("사용자 코드 분석 결과 ", size=30), bgcolor=colors.SURFACE_VARIANT),
            #                 Column(controls=[Text("\n*문제*", size=22),
            #                     Text((await getAnalCode())["문제"]),
            #                     Text("*사용자가 입력한 코드*", size=22),
            #                     Text(user_code_input.value),
            #                     Text("\n*분석 결과*", size=22),
            #                     Text((await getAnalCode())["분석 결과"]),
            #                     ElevatedButton("복습 하러가기", on_click= go_feedback),
            #                     Text("\n\n\n\n",size=15)],
            #                     scroll=ft.ScrollMode.ALWAYS,
            #                     height=700)
            #             ],
            #         )
            #     )
            page.update()

        def view_pop(e):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

        page.on_route_change = route_change
        page.on_view_pop = view_pop

        # 페이지 초기화 및 업데이트
        page.update()

    async def run_ocr_background(self):
        # OCR 작업을 비동기로 실행
        await self.ocr.process_ocr()

if __name__ == "__main__":
    ui = uiMain()
    ft.app(target=ui.main, view=AppView.WEB_BROWSER, assets_dir="assets")

