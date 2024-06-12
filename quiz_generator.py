from langchain_openai import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate,PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain_community.document_loaders import TextLoader, DirectoryLoader

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from langchain.docstore.document import Document
import os
from langchain.prompts import FewShotChatMessagePromptTemplate

class Quizgen:
    def __init__(self):
# FSL 참고용(랭체인) 리펙터링 필요함 그냥 FSL 느낌용 코드라고 봐주세요

        os.environ['OPENAI_API_KEY'] = self.API_KEY
        self.llm = ChatOpenAI(model= "gpt-4o",temperature = .5)

#FSL을 위한 파일 탐색, 폴더 데이터 갯수 만큼 데이터 가져오기
    def count_files_in_folder(self,folder_path):
        files = os.listdir(folder_path)
        
        file_count = 0
        
        for item in files:
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                file_count += 1
        
        return file_count

    #유사도 검색에서 색출된 파일 경로 제공 함수
    def getFolderName(self,indexFile):
        file_path = ''
        if  indexFile == "sort":
            file_path = "./assets/quizGen/sort/"
        #else if indexFile == "if":
        #    file_path = "./quizGen/if"
        
        return file_path

    #색인 기반, 파일 경로를 가지고 FSL에 사용할 프롬포트를 선택해서 json list 형식으로 구성후 반환 코드
    #최종적으로 아래 코드에 영상에서 색인된 도메인(for, if 등등<- 일단 예시)를 파라미터로 함수 호출하면 해당 도메인에 맞는 FSL 생성
    def genFSL_Prompt(self,indexFile):
        self.fewshot_prompt = []
        filePath = self.getFolderName(indexFile)
        for i in range(self.count_files_in_folder(filePath)):
    #        example = open(filePath+indexFile+i+".txt","r",encoding="utf-8")
            with open(filePath+indexFile+str(i)+".txt", 'r',encoding="utf-8") as file:
                json_data = json.load(file)
                self.fewshot_prompt.append(json_data)
                file.close()
        return self.fewshot_prompt


    # 파싱된 JSON 데이터 사용하기
    async def getQuiz(self):
    #FSL Prompt
        FSL_prompt = FewShotChatMessagePromptTemplate(
                    example_prompt= ChatPromptTemplate.from_messages(
                        [
                            ("human","{question}"),
                            ("ai","{answer}")
                        ]
                    ),
                    examples=self.genFSL_Prompt("sort")
                )

        total_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "정렬 알고리즘 관련해서 다음과 같은 유형의 비슷한 문제를 생성해줘"),
                FSL_prompt,
                ("human","문제 줘!"),
            ]
        )
        chain_input = {
            'question' : "정렬 문제 생성해줘"
        }
        self.quizGenerator = LLMChain(
            prompt = total_prompt,
            llm = self.llm,
        ).invoke(chain_input) #실제로는 {detect_subject}으로 탐지 문항 생성
        print(self.quizGenerator['text'])
        return self.quizGenerator['text']
    
    def getQ(self):
        print("getQ 실행")
        return self.quizGenerator['text']

if __name__=="__main__":
    a=Quizgen()
    print(a.getQuiz())