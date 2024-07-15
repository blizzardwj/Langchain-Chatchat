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
from typing import Dict, ClassVar, Any, Optional

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
