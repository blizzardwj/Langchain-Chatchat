"""
File: kb_metadatas.py
Author: blizzardwj
Email: blizzardwj@163.com
Date: 2024-05-07
Description: Knowledge base metadatas service
"""

import os
import re
from datetime import datetime
from typing import Dict

from pydantic import Field

# from configs.metadata_config import ZYY_SENSITIVE_POINTS_DICT, XF_SENSITIVE_POINTS_DICT
from chatchat.server.knowledge_base.kb_metadatas import BaseMetadata, create_example_metadata_subclass

# 敏感点内容字典
ZYY_SENSITIVE_POINTS_DICT = {
    "配方与工艺": {
        "绝密": {
            1: "列为国家重点保护的中医药制剂的配方、生产工艺技术",
            2: "稀有贵细中药材人工合成品的配方、工艺技术"
        },
        "机密": {
            3: "传统中成药的特殊生产工艺和中药饮片炮制的关键技术（含中成药前处理的炮制技术）"
        },
        "秘密": {
            3: "获国家和省、部级科技成果奖励的中医药项目中的关键技术或药物配方",
            4: "已经国家批准的发明项目的技术诀窍及可能成为专利项目的技术内容",
            5: "经县和县以上医疗卫生单位验证，并经省、部级中医药主管部门确认有特殊效果的民间单、验、秘方及诊疗技术诀窍",
            7: "在国际市场上具有一定竞争优势或潜力的中药生产关键工艺技术及药物配方"
        }
    },
    "研发与技术": {
        "机密": {
            1: "未公开的国家级和省、部级中医药科学技术研究、经济贸易的发展规划、计划",
            6: "国家级和部级中医药重点科学技术研究项目的关键技术"
        },
        "秘密": {
            1: "未公开的国家中医药行业发展规划、计划、产业政策及医疗制度改革意见",
            8: "解放后尚未公开出版发行的正在进行研究中的具有重要学术价值的中医药古籍文献",
            12: "通过非公开途径取得的国外科学技术（含资料、样本、样机）及其来源",
            13: "国外已有，但实行技术保密，我国通过研究取得重要进展的技术内容"
        }
    },
    "贸易与市场": {
        "机密": {
            2: "未公布的中医药产品价格改革及调整方案",
            4: "经国家和省主管部门批准的对外贸易、技术转让的谈判意图以及面向国际招标的标底",
            5: "具有重要经济价值的药用动、植物饲养、栽培及防治病虫害的关键技术"
        },
        "秘密": {
            9: "未公开的全国中药产、购、销、存及对外贸易统计资料",
            11: "对外合作中需要承担保密义务的事项"
        }
    },
    "资源与环境": {
        "秘密": {
            2: "全国和省、自治区、直辖市野生药材资源蕴含量及分布资料",
            6: "全国中药产品质量数据库资料"
        }
    },
    "政策与规划": {
        "秘密": {
            14: "未公开的全国中医药事业、基本建设的基本情况报表及设备装备情况统计表。"
        }
    },
    "军需与应急": {
        "机密": {
            7: "国家战备中药的储备点和储备计划"
        },
        "秘密": {
            10: "军需、战备、疫情用中药的运输方案及运输流向"
        }
    },
    "教育与考核": {
        "机密": {
            8: "中医药师、士国家级和省级考试启用前的试题、参考答案和评分标准"
        }
    }
}

XF_SENSITIVE_POINTS_DICT = {
    "社会稳定事项处理": {
        "涉密": {
            1: "泄露后会引起全国或大范围（数个省）社会稳定的重大信访事项的处理方案，决策和工作部署"
        }
    },
    "政治形象保护": {
        "涉密": {
            2: "政治敏感性强，泄露后可能会严重影响党和国家形象的信访事项；揭发检举党和国家领导人未查证问题的信访事项"
        }
    },
    "高级干部调整问题": {
        "涉密": {
            3: "涉及省、部级及其他中央管理的干部调整过程中的重大问题"
        }
    },
    "巨额经济犯罪查办": {
        "涉密": {
            4: "涉及金额巨大的违法违纪和经济犯罪等信访事项及有关查办情况（涉及犯罪嫌疑人外逃问题）"
        }
    },
    "千万级经济案件查办": {
        "涉密": {
            5: "涉及金额巨大的违法违纪和经济犯罪等信访事项及有关查办情况（涉及金额1000万元以上的）"
        }
    },
    "百万级经济案件查办": {
        "涉密": {
            6: "涉及金额巨大的违法违纪和经济犯罪等信访事项及有关查办情况（涉及金额1000万元以下）"
        },
    },
    "重大贪污受贿查办": {
        "涉密": {
            7: "贪污受贿金额巨大，泄露后会影响案件查处工作的信访信息（贪污受贿金额在100万元以上）"
        }
    },
    "小额贪污受贿查办": {
        "涉密": {
            8: "贪污受贿金额巨大，泄露后会影响案件查处工作的信访信息（贪污受贿金额在100万元以下）"
        }
    },
    "大规模群体性事件处理": {
        "涉密": {
            9: "处理政策性强、涉及人数众多，跨地区、跨行业的大规模群体性事件的工作部署和方案"
        }
    },
    "全国群众信访统计": {
        "涉密": {
            10: "全国群众来信来访统计的动态分析及调查研究报告"
        }
    }
}


class ConfidentialPointsMetadata(BaseMetadata):
    doc_type: str = Field(None, title="文档类型")
    confidentiality_level: str = Field(None, title="等级划分")
    sensitive_points: str = Field(None, title="敏感点")
    creation_date: str = Field(None, title="创建日期")

    def do_acquire_metadata(self, **kwargs) -> Dict:
        file_path = kwargs.get("file_path")

        # 获取文件的创建日期（这里使用文件的最后修改时间作为示例）
        stat = os.stat(os.path.expanduser(file_path))
        # stat = os.stat(file_path)
        self.creation_date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

        # 解析文件名称获取文档类型和保密等级
        parts = self.doc_name[:-4].split('-')
        self.doc_type = parts[0]
        self.confidentiality_level, point_number = re.match(r'([^0-9]+)(\d+)', parts[1]).groups()
        point_number = int(point_number)

        # 获取密点内容
        self.sensitive_points = self.get_cls_auxiliary_data().get(self.doc_type, {}).get(self.confidentiality_level,
                                                                                         {}).get(point_number,
                                                                                                 "未发现敏感点")

        # 将元数据和文件内容保存到字典中
        metadata_new = {
            "doc_id": self.doc_id,
            "doc_name": self.doc_name,
            "doc_type": self.doc_type,
            "confidentiality_level": self.confidentiality_level,
            "sensitive_points": self.sensitive_points,
            "creation_date": self.creation_date
        }
        return metadata_new


# class level init: set auxiliary data
# ConfidentialPointsMetadata.set_cls_auxiliary_data(ZYY_SENSITIVE_POINTS_DICT)
ZYYConfidentialPointsMetadata = create_example_metadata_subclass("ZYYConfidentialPointsMetadata",
                                                                 auxiliary_data=ZYY_SENSITIVE_POINTS_DICT,
                                                                 class_template=ConfidentialPointsMetadata)
XFConfidentialPointsMetadata = create_example_metadata_subclass("XFConfidentialPointsMetadata",
                                                                auxiliary_data=XF_SENSITIVE_POINTS_DICT,
                                                                class_template=ConfidentialPointsMetadata)
print(f"Set auxiliary data for {ZYYConfidentialPointsMetadata.__name__}")
print(f"Set auxiliary data for {XFConfidentialPointsMetadata.__name__}")

# Knowledge base and its metadata model
KB_NEED_METADATA = {
    "archive_pos": ZYYConfidentialPointsMetadata,
    "archive_pos_neg": ZYYConfidentialPointsMetadata,
    "xinfang_pos_v2": XFConfidentialPointsMetadata,
}

# test code
if __name__ == "__main__":
    from pathlib import Path
    kb_root = "~/workspace/new_code/Langchain-Chatchat/libs/chatchat-server/chatchat/data/knowledge_base"
    # test ZYYConfidentialPointsMetadata
    metadata1 = ZYYConfidentialPointsMetadata()
    file_info1 = {
        "doc_name": "配方与工艺-秘密4-1.txt",
        "file_path": Path(kb_root).joinpath("archive_pos/content/配方与工艺-秘密4-1.txt")
    }
    metadata_dict1 = metadata1.acquire_metadata(**file_info1)
    print(metadata_dict1)

    # test XFConfidentialPointsMetadata
    metadata2 = XFConfidentialPointsMetadata()
    file_info2 = {
        "doc_name": "巨额经济犯罪查办-涉密4-1.txt",
        "file_path": Path(kb_root).joinpath("xinfang_pos_v2/content/巨额经济犯罪查办-涉密4-1.txt")
    }
    metadata_dict2 = metadata2.acquire_metadata(**file_info2)
    print(metadata_dict2)
