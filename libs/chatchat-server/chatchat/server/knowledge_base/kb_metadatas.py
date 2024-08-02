"""
File: kb_metadatas.py
Author: blizzardwj
Email: blizzardwj@163.com
Date: 2024-05-07
Description: Knowledge base metadatas service
"""

import os
import uuid
from datetime import datetime
import pydantic
from pydantic import BaseModel, Field
from packaging import version
from typing import List, Dict, ClassVar, Any, Optional
from chatchat.server.knowledge_base.model.kb_document_model import DocumentWithVSId

pydantic_v = version.parse(pydantic.__version__)

class BaseMetadata(BaseModel):
    # class level attribute
    if pydantic_v < version.parse("2.0"):
        _auxiliary_data: Dict = {}
    else:
        _auxiliary_data: ClassVar[Dict] = {}

    doc_id: str = Field(None, title="文档ID")
    doc_name: str = Field(None, title="文档名称")

    def __str__(self):
        return f"{self.doc_name} owns metadata"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def set_cls_auxiliary_data(cls, data: Dict):
        if not cls._auxiliary_data:
            cls._auxiliary_data = data
        # cls._auxiliary_data = data

    @classmethod
    def get_cls_auxiliary_data(cls) -> Dict:
        return cls._auxiliary_data

    def acquire_metadata(self, **kwargs) -> Dict[str, Any]:
        """
        method to get metadata according to some rules,
        which is implemented by subclasses.
        """
        # 生成文件的唯一ID
        self.doc_id = str(uuid.uuid4())
        self.doc_name = kwargs.get("doc_name")
        metadata_new = self.do_acquire_metadata(**kwargs)
        return metadata_new

    def do_acquire_metadata(self, **kwargs) -> Dict[str, Any]:
        """
        Method for subclasses to implement specific metadata acquisition.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class ExampleMetadata(BaseMetadata):
    """
    User customized metadata class.
    """
    doc_type: str = Field(None, title="文档类型")
    level: str = Field(None, title="等级")
    category: str = Field(None, title="类别")
    creation_date: str = Field(None, title="创建日期")

    def do_acquire_metadata(self, **kwargs) -> Dict:
        """
        method to get metadata according to some rules,
        overriding the parent class method.
        """
        file_path = kwargs.get("file_path")

        # 获取文件的创建日期（这里使用文件的最后修改时间作为示例）
        stat = os.stat(os.path.expanduser(file_path))
        # stat = os.stat(file_path)
        self.creation_date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

        # 解析文件名称获取文档类型
        parts = self.doc_name[:-4].split('_')
        self.doc_type = parts[0]
        self.level = self.get_cls_auxiliary_data().get("level")

        # 获取类别
        self.category = self.get_cls_auxiliary_data().get("category")

        # 将元数据和文件内容保存到字典中
        metadata_new = {
            "doc_id": self.doc_id,
            "doc_name": self.doc_name,
            "doc_type": self.doc_type,
            "level": self.level,
            "category": self.category,
            "creation_date": self.creation_date
        }
        return metadata_new


# subclass factory
def create_example_metadata_subclass(name: str,
                                          auxiliary_data: Optional[Dict] = None,
                                          class_template=ExampleMetadata) -> BaseMetadata:
    """
    Factory function to create a subclass of example metadata.
    """
    # create a new class
    new_class = type(name, (class_template,), {})
    # set auxiliary data
    if auxiliary_data:
        new_class.set_cls_auxiliary_data(auxiliary_data)
    else:
        print("no auxiliary data set for class {name}")

    return new_class

TYPE1_DICT = {
    "level": "ordinary",
    "category": "personal",
}

TYPE2_DICT = {
    "level": "critical",
    "category": "business",
}

# class level init: set auxiliary data
Type1Metadata = create_example_metadata_subclass("Type1Metadata",
                                                auxiliary_data=TYPE1_DICT,
                                                class_template=ExampleMetadata)
Type2Metadata = create_example_metadata_subclass("Type2Metadata",
                                                auxiliary_data=TYPE2_DICT,
                                                class_template=ExampleMetadata)
print(f"Set auxiliary data for {Type1Metadata.__name__}")
print(f"Set auxiliary data for {Type2Metadata.__name__}")

# Assign which Knowledge base needs its metadata model
KB_NEED_METADATA = {
    "Type1_kb": Type1Metadata,
    "Type2_kb": Type2Metadata,
}


class SampleContextProcessor:
    """
    Get context for analysis from sample metadata
    """

    def __init__(self, metadata_keys: List[str]):
        self.selected_items = metadata_keys

    def set_sample_source(self, kb_name: str, docs: List[DocumentWithVSId]):
        self.kb_name = kb_name
        self.docs = docs
        self.expander_context = []

    @staticmethod
    def format_dict_to_string(data_dict: Dict, keys: List[str]):
        """
        Formats selected keys from a dictionary into a specific string format.
        Note: just one piece of information in one paragraph

        Args:
        data (dict): The dictionary from which to extract the data.
        keys (list): A list of keys which are to be included in the output string.

        Returns:
        str: A formatted string containing selected key-value pairs.
        """
        lines = []
        for _, key in enumerate(keys):
            if key in data_dict:
                lines.append(f"- {key}: {data_dict[key]}")
        return "\n".join(lines) + "\n\n"

    def _get_metadata_dict_from_VSdoc(self, kb_name: str, doc: DocumentWithVSId):
        # get metadata from a document in vector store
        metadata_dict = doc.metadata.get(KB_NEED_METADATA[kb_name].__name__, "")
        return metadata_dict

    def get_sample_context(self, info_keys: List[str] = []) -> str:
        # get multiple pieces of information to construct for RAG (return value) and expander (in UI)
        if not info_keys:
            self.selected_items = info_keys
        # else use selected items in init
        sample_context = []
        for idx, doc in enumerate(self.docs):
            metadata_dict = self.get_metadata_dict_from_VSdoc(self.kb_name, doc)
            one_piece = self.format_dict_to_string(metadata_dict, info_keys)
            sample_context.append(f"Metadata {idx + 1}:\n\n{one_piece}")
        self.expander_context = sample_context
        return "".join(sample_context)


SELECTED_METADATA_KEYS = ["level", "category"]
context_processor = SampleContextProcessor(metadata_keys=SELECTED_METADATA_KEYS)
# context_processor.set_sample_source("kb_name", docs)
# context_for_llm = context_processor.get_sample_context()
# expander_context = context_processor.expander_context


# test code
if __name__ == "__main__":
    # test Type2Metadata
    metadata1 = Type1Metadata()
    file_info1 = {
        "doc_name": "type1_file.txt",
        "file_path": "~/workspace/new_code/Langchain-Chatchat/libs/chatchat-server/chatchat/data/knowledge_base/Type1_kb/content/type1_file.txt"
    }
    metadata_dict1 = metadata1.acquire_metadata(**file_info1)
    print(metadata_dict1)

    # test Type2Metadata
    metadata2 = Type2Metadata()
    file_info2 = {
        "doc_name": "type2_file.txt",
        "file_path": "~/workspace/new_code/Langchain-Chatchat/libs/chatchat-server/chatchat/data/knowledge_base/Type2_kb/content/type2_file.txt"
    }
    metadata_dict2 = metadata2.acquire_metadata(**file_info2)
    print(metadata_dict2)
