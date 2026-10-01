import pdfplumber
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from pathlib import Path

CHROMA_PATH      = "./chroma_db"
COLLECTION_NAME  = "annual_reports"
CHUNK_SIZE       = 800
CHUNK_OVERLAP    = 150
EMBED_MODEL      = "nomic-embed-text"

def load_pdf(file_path:str,company:str,year:int)->list[str]:
    pages=[]
    paths=Path(file_path)

    print(f"Loading PDF file: {paths}")

    with pdfplumber.open(paths) as p:
        total=len(p.pages)
        for i,page in enumerate(p.pages,start=1):
            text=page.extract_text()
            if not text or not text.strip():
                continue

            pages.append({
                "text":text,
                "metadata":{
                    "company":company,
                    "year":year,
                    "page_number":i,
                    "source":paths.name
                }
            })

            print(f"Loaded page {i}/{total} from {paths.name}")

    return pages
def chunk_pages(pages:list[dict])->list[dict]:
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n","\n"," ",""]
    )
    chunks=[]
    for page in pages:
        split_text=splitter.split_text(page["text"])
        for idx,chunk_split in enumerate(split_text,start=1):
            if not chunk_split or not chunk_split.strip():
                continue
            chunks.append({
                "id":f"{page['metadata']['source']}_page_{page['metadata']['page_number']}_chunk_{idx+1}",
                "text":chunk_split,
                "metadata":{
                    **page["metadata"],
                    "chunk_number":idx
                }
            })

    print(f"Total chunks created: {len(chunks)}")
    return chunks

def get_collection()->chromadb.Collection:
    client=chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False)
    )
    collection=client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description":"Annual reports collection"}
    )
    print(f"Collection '{COLLECTION_NAME}' is ready.")
    return collection

def embed_store(chunks:list[dict])->None:
    embedings=OllamaEmbeddings(model=EMBED_MODEL)
    collection=get_collection()
    texts=[c["text"] for c in chunks]
    ids=[c["id"] for c in chunks]
    metadatas=[c["metadata"] for c in chunks]

    print(f"Embedding and storing {len(chunks)} chunks...")

    batch_size=50
    for i in range(0,len(chunks),batch_size):
        batch_texts=texts[i:i+batch_size]
        batch_ids=ids[i:i+batch_size]
        batch_metadatas=metadatas[i:i+batch_size]

        vectors=embedings.embed_documents(batch_texts)

        collection.upsert(
            ids=batch_ids,
            embeddings=vectors,
            documents=batch_texts,
            metadatas=batch_metadatas
        )
        print(f"Stored chunks {i+1} to {min(i+batch_size,len(chunks))}")
    print("All chunks have been embedded and stored successfully.")


def ingest(file_path:str,company:str,year:int)->None:
    pages=load_pdf(file_path,company,year)
    chunks=chunk_pages(pages)
    embed_store(chunks)
    print(f"Ingestion completed for {file_path} with {len(chunks)} chunks.")

def verify(query: str, company: str) -> None:
    collection = get_collection()

    from langchain_ollama import OllamaEmbeddings
    embeddings   = OllamaEmbeddings(model=EMBED_MODEL)
    query_vector = embeddings.embed_query(query)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=3,
        where={"company": company},
    )

    print(f"\nTest query: '{query}'")
    for i, (doc, meta) in enumerate(
        zip(results["documents"][0], results["metadatas"][0])
    ):
        print(f"\nResult {i+1} | Page {meta['page_number']}")
        print(doc[:200])


if __name__ == "__main__":
   ingest(
        file_path="data\\reports\\Customer Service - How to download and install Firefox on Windows_1736eb5306334b6fb69e3f804a3bd060.pdf",
        company="Firefox",
        year=2024
    )
   verify("how to install firefox?", "Firefox")
