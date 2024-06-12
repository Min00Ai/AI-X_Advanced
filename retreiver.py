import os
import json
from datetime import datetime
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA


# JSON 파일 디렉토리 경로
directory_path = './script_data'

# 모든 JSON 파일 로드
def load_json_files(directory_path):
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    for text in item["related_speech_texts"]:
                        doc = Document(
                            page_content=text,
                            metadata={
                                "code_start_timestamp": item["code_start_timestamp"],
                                "code_end_timestamp": item["code_end_timestamp"],
                                "code_text": item["code_text"],
                                "topic": item["topic"]
                            }
                        )
                        documents.append(doc)
    return documents

# 문서 로드, 색인
def load_and_index_documents(directory_path, chunk_size=300, chunk_overlap=0):
    documents = load_json_files(directory_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(docs, embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3},) 
    return retriever

# chain 초기화
class rtv_chain():
    def __init__(self):
        self.chat = ChatOpenAI(model_name="gpt-4", temperature=0.21)
        self.directory_path = directory_path
        self.retriever = load_and_index_documents(self.directory_path)
    
    def search_vulnerability(self, query):
        qa_chain = RetrievalQA.from_chain_type(llm=self.chat, retriever=self.retriever, return_source_documents=True)
        result = qa_chain.invoke({"query": query})
        return result

# 쿼리 입력 및 타임스탬프 검색
def getrtv(query):
    llm = rtv_chain()
    query = query
    result = llm.search_vulnerability(query)

    if result and 'source_documents' in result:
        source_doc = result['source_documents'][0]
        print(f"Code Start Timestamp: {source_doc.metadata['code_start_timestamp']}")
        print(f"Code End Timestamp: {source_doc.metadata['code_end_timestamp']}")
        print(f"Topics : {source_doc.metadata['topic']}")
        return source_doc.metadata['code_start_timestamp'],source_doc.metadata['code_end_timestamp'],source_doc.metadata['topic']
    else:
        print("No relevant code found.")