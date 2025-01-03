Project - AI+X 고급반
팀장 - 이정민
- 주제
  - 코딩 인터넷 강의 학습 효율성 증가 서비스

- 사용 기술
  - OCR, ASR, LLM(GPT API + Langchain), Object Detection(YOLOv9)

- Architecture
  - YOLOv9 기반 인터넷 강의 속 코딩 화면 Detection 실시
  - 코딩 화면 속 코드 내용 OCR을 통해 내용 추출
  - OCR 실행 Timestamp 및 해당 강의 내용을 Text로 저장(with ASR)
    - 예 1
    - time: xx:xx
    - text: ["오늘은 파이썬에 대해 배우겠습니다","...", ...]
    - ocr_result: ["import os","...", ...]
  - 사용자에게 효율적 학습 경험 제공
    - 복습할 부분 영상 검색 기능
    - Text와 OCR 결과(Code)를 활용한 유사 코딩테스트 문제 제공
