import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import re
from config import model

"""
# PDF
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("file.pdf")

# DOCX
from langchain_community.document_loaders import Docx2txtLoader
loader = Docx2txtLoader("file.docx")

# YouTube транскрипт
from langchain_community.document_loaders import YoutubeLoader
loader = YoutubeLoader.from_youtube_url("https://youtube.com/...")

"""
bs4_strainer = bs4.SoupStrainer("div", id=lambda x: x and x.startswith("articleBody_"))

# Возращает список объектов Document с метаданными source который указывает на источник документа (ссылка сайта).
# doc.page_content сам текст 
# doc.metadata словарь с метаданными
loader = WebBaseLoader(
    web_path="https://lenta.ru/articles/2026/04/06/luchshie-dramy-vseh-vremen/",
    bs_kwargs={"parse_only": bs4_strainer}
)

docs = loader.load()

for doc in docs:
    doc.page_content = re.sub(r'\n+', ' ', doc.page_content).strip()

print(f"Total characters: {len(docs[0].page_content)}")
print(docs[0].page_content)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)

all_splits = text_splitter.split_documents(docs)

print(f"Total splits: {len(all_splits)}")

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3",
                                   model_kwargs={"device": "cpu"},
                                   encode_kwargs={"normalize_embeddings": True},
)

vector_store = Chroma(
    collection_name="lenta-articles",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

ids = vector_store.add_documents(all_splits)
# print(ids) Выводит uuid каждого добавленного документа в векторное хранилище. Полезно для отладки.

print(f"Total documents in vector store: {len(ids)}")

print(f"Всего векторов в базе {vector_store._collection.count()}") # Выводит общее колличество векторов в коллекции Chroma.

results = vector_store._collection.get()
print(results["metadatas"])
# print(results["documents"]) показывает текст всех документов. Полезно для отладки и удаления символов переноса строки.
# print(results["ids"]) показывает uuid всех документов.

