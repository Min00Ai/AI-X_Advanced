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
      - RAG을 적용하여 위에 Text로 저장한 Docs에서 복습 부분의 Time 값 가져옴
      - Web UI 상, 동영상을 해당 Time 값으로 이동하여 복습 진행
    - Text와 OCR 결과(Code)를 활용한 유사 코딩테스트 문제 제공
      - crawling을 통해 코딩 테스트 문제 생성 및 저장
      - 만든 문제를 주제 별로 DB에 저장하여 LLM(Few-shot)을 이용하여 다양한 문제 생성 및 제공 
