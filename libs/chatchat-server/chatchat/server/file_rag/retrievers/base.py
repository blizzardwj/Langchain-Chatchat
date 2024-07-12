from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Any

from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langchain_core.documents.base import Document


class BaseRetrieverService(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.do_init(**kwargs)

    @abstractmethod
    def do_init(self, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def from_vectorstore(
        vectorstore: VectorStore,
        top_k: int,
        score_threshold: int or float,
    ):
        pass

    @abstractmethod
    def get_relevant_documents(self, query: str):
        pass


class CustomVectorStoreRetriever(VectorStoreRetriever):
    """
    Can retrun Document instances with similarity scores.
    DO NOT create instance directly:
    1. It is common to create a VectorStoreRetriever instance from a VectorStore instance.
    2. Use from_instance method to create a new instance instead.
    """
    @classmethod
    def from_instance(cls, instance: VectorStoreRetriever) -> 'CustomVectorStoreRetriever':
        """
        Create a new CustomVectorStoreRetriever instance from an existing VectorStoreRetriever instance.
        """
        new_instance = cls.__new__(cls)
        new_instance.__dict__.update(instance.__dict__)
        return new_instance

    def _get_relevant_documents(self, query: str, *, run_manager: Any):# -> List[Tuple[Document, float]]:
        """
        Override VectorStoreRetriever's _get_relevant_documents method to return the top_k documents.
        """
        if self.search_type == "similarity_score_threshold":
            docs_and_similarities = (
                self.vectorstore.similarity_search_with_relevance_scores(
                    query, **self.search_kwargs
                )
            )
        else:
            docs = super()._get_relevant_documents(query, run_manager=run_manager)
            docs_and_similarities = [(doc, 0) for doc in docs]

        return docs_and_similarities

