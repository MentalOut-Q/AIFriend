import lancedb
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import LanceDB
from langchain_text_splitters import RecursiveCharacterTextSplitter

from web.documents.utils.custom_embeddings import CustomEmbeddings

def insert_documents():
    loader = TextLoader ('./web/documents/data.txt', encoding='utf-8')
    documents = loader. load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    print(f"已切分成 {len(texts)}个片段。")

    embeddings = CustomEmbeddings()
    db = lancedb.connect('./web/documents/lancedb_storage')
    vector_db = LanceDB.from_documents(
        documents=texts,
        embedding=embeddings,
        connection=db,
        table_name='my_knowledge_base',
        mode='overwrite',
    )
    print(f"已插入 {vector_db._table.count_rows()}行数据。")

def insert_character_story(character_id: int, file_path: str):
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()
    texts = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    ).split_documents(documents)
    for t in texts:
        t.metadata['character_id'] = character_id

    embeddings = CustomEmbeddings()
    db = lancedb.connect('./web/documents/lancedb_storage')
    LanceDB.from_documents(
        documents=texts,
        embedding=embeddings,
        connection=db,
        table_name=f'character_{character_id}_kb',
        mode='overwrite',
    )