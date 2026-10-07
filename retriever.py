import chromadb
import os
import cohere
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from dotenv import load_dotenv
load_dotenv()

CHROMA_PATH     = "./chroma_db"
COLLECTION_NAME = "annual_reports"
EMBED_MODEL     = "nomic-embed-text"
COHERE_API_KEY  = os.environ.get("COHERE_API_KEY", "")

def get_vectorstore()->Chroma:
    embbedings=OllamaEmbeddings(model=EMBED_MODEL)
    vectorestore=Chroma(
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME,
        embedding_function=embbedings
    )
    count=vectorestore._collection.count()
    print(f"Vectorstore loaded with {count} documents.")
    return vectorestore

def get_all_documents(vectorstore:Chroma)->list[dict]:
    all_data=vectorstore.get()
    documents=[
        Document(
            page_content=text,
            metadata=metadata
        )
        for text,metadata in zip(
            all_data["documents"],
            all_data["metadatas"]
        )
    ]
    print(f"Loaded {len(documents)} documents for BM25")
    return documents

def build_retriever(company:str=None,top_k:int=5)->EnsembleRetriever:
    vectorestores=get_vectorstore()
    documents=get_all_documents(vectorestores)

    if company :
       documents=[ d for d in documents 
                  if d.metadata.get("company","").lower()==company.lower()]
    print(f"Filtered to {len(documents)} chunks for {company}")

    bm25_retriver=BM25Retriever.from_documents(documents)
    bm25_retriver.k=top_k

    search_kwargs={"k":top_k}
    if company:
        search_kwargs["filter"]={"company":company}
    vectore_retriver=vectorestores.as_retriever(
        search_type="mmr", 
        search_kwargs=search_kwargs)
    ensemble=EnsembleRetriever(retrievers=[bm25_retriver,vectore_retriver],weights=[0.4,0.6])
    print(f"Hybrid retriever ready (BM25 40% + Vector 60%)")
    return ensemble

def rerank(query:str,document:list[Document],top_n:int=5)->list[Document]:
     if not COHERE_API_KEY:
        print("No Cohere key — skipping rerank, returning top_n as-is")
        return document[:top_n]

     co=cohere.Client(COHERE_API_KEY)
     result=co.rerank(
         query=query,
         documents=[d.page_content for d in document],
         top_n=top_n,
         model="rerank-v3.5"
     )

     reranked=[document[r.index] for r in result.results]
     print(f"Reranked {len(document)} → top {top_n}")
     return reranked

def format_documents(document:list[Document])->str:
    formatted=[]
    for doc in document:
        company = doc.metadata.get("company", "Unknown")
        page    = doc.metadata.get("page",    "?")

        formatted.append(
            f"[{company}, Page {page}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(formatted)

def retrive(query:str,company:str=None,top_k:int=5)->str:
    """Full retrieval pipeline:
    1. Hybrid search (BM25 + vector)
    2. Cohere rerank
    3. Format with citations

    Returns context string ready for LLM."""
    print(f"Retrieving for query: {query} (company={company}, top_k={top_k})")

    # 1. Hybrid search
    retrive=build_retriever(company=company,top_k=top_k)
    doc=retrive.invoke(query)
    print(f"Retrieved {len(doc)} chunks from hybrid search")

    # 2. Cohere rerank
    doc=rerank(query=query,document=doc,top_n=top_k)

    # 3. Format with citations
    context=format_documents(doc)

    return context


if __name__ == "__main__":
    context = retrive(
        query="how to install the firefox?",
        company="firefox",
        top_k=5,
    )
    print("\n--- Retrieved Context ---")
    print(context)