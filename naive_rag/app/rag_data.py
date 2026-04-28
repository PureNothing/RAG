import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from app.config import model

bs4_strainer = bs4.SoupStrainer(class_("post-title", "post-header", "post-content"))

loader = WebBaseLoader(
    web_path="https://lenta.ru/articles/2026/04/06/luchshie-dramy-vseh-vremen/",
    bs_kwargs={"parse_only": bs4_strainer}
)

docs = loader.load()

print(f"Total characters: {len(docs[0].page_content)}")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)

all_splits = text_splitter.split_documents(docs)

print(f"Total splits: {len(all_splits)}")

embeddings = OpenAIEmbeddings(model="bge_m3")

vector_store = Chroma(
    collection_name="lenta-articles",
    embedding_function=embeddings,
    persist_directory="/chroma_db",
)

ids = vector_store.add_documents(all_splits)

print(f"Total documents in vector store: {len(ids)}")
