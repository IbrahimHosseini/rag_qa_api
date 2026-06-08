from langchain_text_splitters import RecursiveCharacterTextSplitter


async def split_text(text: str, chunk_size:int=1000, overlap:int=200) -> list[str]:
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    splitter.split_text(text=text)