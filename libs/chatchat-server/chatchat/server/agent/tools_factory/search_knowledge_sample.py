"""
File: search_knowledge_sample.py
Author: blizzardwj
Email: blizzardwj@163.com
Date: 2024-07-05
Description: Search knowledge sample tool. Samples are knowledge file with multiple metadata.
"""

from chatchat.server.agent.tools_factory.tools_registry import (
    BaseToolOutput,
    regist_tool,
)
from chatchat.server.knowledge_base.kb_api import list_kbs
from chatchat.server.knowledge_base.kb_doc_api import DocumentWithVSId, search_docs
from chatchat.server.pydantic_v1 import Field
from chatchat.server.utils import get_tool_config

KB_SAMPLE_INFO = ({"archive_pos": "中医药正样本",
                "archive_pos_neg": "中医药正负样本",
                "xinfang_pos_v2": "xinfang正样本 v2",})
template = (
    "Use knowledge samples from one or more of these:\n{KB_info}\n to get information，Only local data on "
    "this knowledge use this tool. The 'database' should be one of the following: [{key}]."
)
KB_info_str = "\n".join([f"{key}: {value}" for key, value in KB_SAMPLE_INFO.items()])
knowledge_sample_des = template.format(KB_info=KB_info_str, key=list(KB_SAMPLE_INFO.keys()))


class KBToolOutput(BaseToolOutput):
    def __str__(self) -> str:
        context = ""
        docs = self.data["docs"]
        source_documents = []

        for inum, doc in enumerate(docs):
            doc = DocumentWithVSId.parse_obj(doc)
            source_documents.append(doc.page_content)

        if len(source_documents) == 0:
            context = "没有找到相关文档,请更换关键词重试"
        else:
            for doc in source_documents:
                context += doc + "\n\n"

        return context


def do_search_knowledge_sample(query: str, database: str, config: dict):
    docs = search_docs(
        query=query,
        knowledge_base_name=database,
        top_k=config["top_k"],
        score_threshold=config["score_threshold"],
    )
    return {"knowledge_base": database, "docs": docs}


@regist_tool(description=knowledge_sample_des, title="高级样本库")
def search_knowledge_sample(
    database: str = Field(
        description="Database for Knowledge Search",
        choices=[kb.kb_name for kb in list_kbs().data],
    ),
    query: str = Field(description="Query for Knowledge Search"),
):
    """
    Search knowledge samples for context expension
    """
    tool_config = get_tool_config("search_knowledge_sample")
    ret = do_search_knowledge_sample(query=query, database=database, config=tool_config)
    return KBToolOutput(ret, database=database)