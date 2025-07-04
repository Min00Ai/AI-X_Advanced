# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 15:10:19 2024

@author: user
"""

from langchain_openai.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import SystemMessagePromptTemplate,PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_community.document_loaders import TextLoader, DirectoryLoader

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
import os
from langchain.prompts import FewShotChatMessagePromptTemplate

import difflib


#코드 분석을 위한 Langchain Tuning
#기본 틀:
#   LLM에게 Prompt로 사용자가 입력한 Python 코드를 제공
#   LLM의 Response로 사용자의 Python 코드 분석 결과를 받음
#   **Response인 코드 분석 결과에 대한 구체적인 틀은 회의 필요
#   코드 분석의 FLOW는 어떻게 진행할 것인가 EX) 1. Syntex Error가 있는가
#   --> 2. Algo가 효율적으로 되어 있는가 --> 3. 코드에서 필요없는 부분이 있는가 --> 4. 등...

### 주의사항
#코드 작성은 이해를 위해 주석을 가능한 추가하고
#사용성 좋게 객체화 할 것

class Analysis_Code:
    def __init__(self):
        #Openai API 키 등록

        os.environ['OPENAI_API_KEY'] = self.API_KEY
        #LLM 호출 / 정확성을 높이기 위해 GPT-4모델 사용, temperature은 0.1
        self.llm = ChatOpenAI(model="gpt-4")
        
    # Response를 튜닝하기 위한 프롬프트 지정    
    def setPrompt(self):
        #promtp는 위 "기본 틀" 에서 코드 분석 FLOW는 아래 분석 방법에 구체적으로 작성할 것
        self.prompt =   """
                        Python Code 문제와 사용자가 작성한 정답 코드를 보여줄테니 코드에 대해서 분석을 하고 분석 결과를 보여줄 것.
                        코드는 Python 언어로 이루어진 코드이며 아래의 분석 방법에 따라 분석할 것.
                        답변을 할때에는 답변 형식에 맞춰 답변할 것.

                        분석 방법:
                        우선 문제에 대한 정답으로 작성된 코드가 맞는지 확인할 것.
                        문제와 관련된 코드가 아니면 코드에 대한 간단한 해석과 문제가 요구하는 의도를 정리해서 보여줄 것.
                        문제와 관련된 코드가 맞다면 문법적으로 오류가 있는지 확인할 것.
                        문법적 오류가 있다면 해당 부분과 Solution을 제공할 것.
                        문법적 오류가 없다면 알고리즘을 효율적으로 작성했는지 확인할 것.
                        만약 알고리즘 측면에서 일반적으로 더 효율적인 알고리즘이 있다면 코드에서 비효율적인 부분을 사용자에게 알려주고 보다 효율적인 알고리즘을 소개할 것.
                        마지막으로 코드에서 사용되지 않거나 불필요하게 작성된 부분이 있다면 어떤 부분이 왜 불필요한지 사용자에게 알려줄 것.
                        
                        답변 형식:   
                        분석 방법에 따라 분석한 결과를 바탕으로 답변할 것. 
                        사용자가 제공한 코드를 바탕으로 답변할 것.
                        분석 과정에서 사용자의 코드를 수정해서 답변으로 보여주지 말 것.
                        답변은 사용자의 코드 중 어느 부분이 개선되면 좋을 것 같은지 알려줄 것.
                        출력 형식은 Json으로 파싱할 수 있도록 Json 형태의 문자열로 제공할 것.
                        Json의 Key 값으로는 아래 예시와 같이 "문제, 분석 결과, 권장 알고리즘"으로 구성해서 제공할 것.
                        권장 알고리즘은 분석 과정에서 더 효율적인 알고리즘이 있으면 작성하고 더 효율적인 알고리즘이 없다면 value에 0을 넣어 제공할 것.
                        아래의 출력 예시를 참고해서 답변할 것.
                        *중요* 출력은 JSON형식으로 답하고 각 문장은 줄바꿈으로 잘 표현할 것.
                        *중요* 문제는 요약해서 한줄로 표현할 것.
                        *중요* 출력에서 딕셔너리 형태의 문제, 분석 결과, 권장 알고리즘을 제외한 추가적인 너의 답변은 절대 하지 말 것.
                        *중요* 출력에는 문제, 분석 결과, 권장 알고리즘은 무조건 존재할 것! 나머지는 존재하지 말 것!
                        *중요* 출력 예시를 벗어나는 답변(추가 수정된 코드나 조언, 힌트 등)은 절대 하지 말 것.
                        *중요* 권장 알고리즘은 [퀵 정렬, 선택 정렬, 삽입 정렬, 계수 정렬] 안에 해당하는 내용이 없으면 0을 출력하고 해당하는 내용이 있으면 해당 단어만 출력할 것.
                        *중요* 권장 알고리즘은 0이 아니라면 한가지의 알고리즘만 알려 줄 것.

                        출력 예시:
                        "분석 결과": "1. 문제에 적합한 코드를 작성하셨습니다.
                                    2. Syntax Error 문제가 없이 잘 동작하는 코드를 작성했습니다.
                                    3. 그러나 리스트 정렬 알고리즘에서 문제의 크기(N)에 따라 시간복잡도가 효율적인 퀵, 병합 정렬을 사용하는 것을 권장합니다.
                                    4. 코드에서 2번 째 줄인 "num = 0"은 사용하지 않는 코드로 지우는 것을 권장합니다."
                        "권장 알고리즘": "퀵 정렬"
                        """
        self.promptF = ChatPromptTemplate.from_messages([
                    ("system",self.prompt),
                    ("ai","다음 기준에 맞춰 코드 분석을 진행해 드릴게요 코드를 제시해주세요."),
                    ("human","{question}"),
        
        ])                
            
        
    def setChain(self):
        self.code_Chain = LLMChain(
            prompt = self.promptF,
            llm=self.llm)
        
        
    def getResponse(self,quiz,user_code):
        self.input = f" 문제 : {quiz} \n\n 사용자 코드:\n {user_code}"
        chain_input = {
            'question' : self.input
            }
        self.response = self.code_Chain.invoke(chain_input)
        return self.response['text']

    def getAC(self):
        print("getAC 실행")
        print(self.response['text'])
        return self.response['text']
    
    async def run(self,quiz, user_code):
        self.setPrompt()
        self.setChain()
        return self.getResponse(quiz, user_code)


    def analyze_code(self, user_code):
        self.set_prompt(user_code)
        # ask 메서드를 사용하여 GPT-4에게 프롬프트를 보내고 응답을 받습니다.
        response = self.llm.ask(self.prompt)
        return response


# if __name__=="__main__":
#     analyzer = Analysis_Code()
#     quiz = "0부터 100까지 출력하는 반복문 작성하세요"  # 실제 생성된 퀴즈 문제를 넣을거에요.
#     user_code = "for i in rnage(100):\n pront(i)"   # 실제 사용자가 작성한 코드를 넣을거에요.
#     analyzer.run(quiz,user_code)
