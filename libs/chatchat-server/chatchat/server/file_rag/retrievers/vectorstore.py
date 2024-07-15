from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langchain_core.retrievers import BaseRetriever

from chatchat.server.file_rag.retrievers.base import BaseRetrieverService, CustomVectorStoreRetriever
from langchain_community.vectorstores.chroma import Chroma


class VectorstoreRetrieverService(BaseRetrieverService):
    def do_init(
        self,
        retriever: BaseRetriever = None,
        top_k: int = 5,
    ):
        self.vs = None
        self.top_k = top_k
        self.retriever = retriever

    @staticmethod
    def from_vectorstore(
        vectorstore: VectorStore,
        top_k: int,
        score_threshold: int or float,
    ):
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            # search_type="similarity",
            search_kwargs={"score_threshold": score_threshold, "k": top_k},
        )
        retriever = CustomVectorStoreRetriever.from_instance(retriever)
        return VectorstoreRetrieverService(retriever=retriever)

    def get_relevant_documents(self, query: str):
        # return self.retriever.get_relevant_documents(query)[: self.top_k]
        return self.retriever.invoke(query)[: self.top_k]
