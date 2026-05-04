"""
岗位画像模块 - 使用大模型构建岗位画像
"""

import json
from typing import Dict, List, Optional
import re


class JobProfileGenerator:
    """岗位画像生成器"""
    
    # 10大核心岗位的预定义画像（可直接使用）
    JOB_PROFILES = {
        "Java开发工程师": {
            "岗位名称": "Java开发工程师",
            "专业技能": {
                "编程语言": ["Java", "Kotlin", "Scala"],
                "后端框架": ["SpringBoot", "SpringCloud", "MyBatis", "Hibernate"],
                "数据库": ["MySQL", "Oracle", "PostgreSQL", "Redis"],
                "消息队列": ["RabbitMQ", "Kafka", "RocketMQ"],
                "容器技术": ["Docker", "Kubernetes"],
                "构建工具": ["Maven", "Gradle", "Jenkins"]
            },
            "证书要求": {
                "必备": [],
                "推荐": ["软考中级（软件设计师）", "OCP（Oracle认证专家）", "PMP项目管理师"]
            },
            "软技能": {
                "抗压能力": "高",
                "沟通能力": "中",
                "学习能力": "高",
                "团队协作": "高",
                "创新能力": "中"
            },
            "学历要求": {
                "最低": "本科",
                "理想": "硕士"
            },
            "经验要求": {
                "初级": "1-3年",
                "中级": "3-5年",
                "高级": "5年+"
            },
            "薪资范围": {
                "初级": "8K-15K",
                "中级": "15K-25K",
                "高级": "25K-50K"
            },
            "工具技能": ["Git", "SVN", "IDEA", "Eclipse", "Navicat", "Linux"],
            "行业发展趋势": "云原生、微服务架构、Serverless、DDD领域驱动设计"
        },
        
        "前端开发工程师": {
            "岗位名称": "前端开发工程师",
            "专业技能": {
                "编程语言": ["HTML5", "CSS3", "JavaScript", "TypeScript"],
                "前端框架": ["Vue.js", "React", "Angular", "Svelte"],
                "UI框架": ["Element UI", "Ant Design", "Bootstrap", "Tailwind CSS"],
                "构建工具": ["Webpack", "Vite", "Rollup", "Gulp"],
                "状态管理": ["Vuex", "Pinia", "Redux", "MobX"],
                "移动开发": ["React Native", "Flutter", "uni-app"]
            },
            "证书要求": {
                "必备": [],
                "推荐": ["软考初级", "前端工程师认证"]
            },
            "软技能": {
                "抗压能力": "中",
                "沟通能力": "高",
                "学习能力": "高",
                "审美能力": "中",
                "创新能力": "高"
            },
            "学历要求": {
                "最低": "本科",
                "理想": "本科"
            },
            "经验要求": {
                "初级": "1-3年",
                "中级": "3-5年",
                "高级": "5年+"
            },
            "薪资范围": {
                "初级": "8K-15K",
                "中级": "15K-22K",
                "高级": "22K-40K"
            },
            "工具技能": ["VS Code", "Figma", "Sketch", "Postman", "Chrome DevTools"],
            "行业发展趋势": "跨端开发、低代码平台、WebAssembly、AI辅助编程"
        },
        
        "Python开发工程师": {
            "岗位名称": "Python开发工程师",
            "专业技能": {
                "编程语言": ["Python"],
                "Web框架": ["Django", "Flask", "FastAPI", "Tornado"],
                "数据处理": ["Pandas", "NumPy", "SciPy"],
                "数据库": ["MySQL", "PostgreSQL", "MongoDB", "Redis"],
                "爬虫技术": ["Scrapy", "Selenium", "Requests"],
                "机器学习": ["Scikit-learn", "TensorFlow", "PyTorch"]
            },
            "证书要求": {
                "必备": [],
                "推荐": ["软考中级", "AWS认证", "PMP"]
            },
            "软技能": {
                "抗压能力": "中",
                "沟通能力": "中",
                "学习能力": "高",
                "逻辑思维": "高",
                "创新能力": "中"
            },
            "学历要求": {
                "最低": "本科",
                "理想": "硕士"
            },
            "经验要求": {
                "初级": "1-3年",
                "中级": "3-5年",
                "高级": "5年+"
            },
            "薪资范围": {
                "初级": "10K-18K",
                "中级": "18K-28K",
                "高级": "28K-45K"
            },
            "工具技能": ["PyCharm", "Jupyter Notebook", "Git", "Docker"],
            "行业发展趋势": "AI应用开发、数据工程、自动化运维、Serverless"
        },
        
        "软件测试工程师": {
            "岗位名称": "软件测试工程师",
            "专业技能": {
                "测试理论": ["黑盒测试", "白盒测试", "灰盒测试", "测试用例设计"],
                "自动化测试": ["Selenium", "Appium", "Postman", "JUnit", "TestNG"],
                "性能测试": ["JMeter", "LoadRunner", "Locust"],
                "接口测试": ["SoapUI", "RestAssured", "Charles"],
                "数据库": ["MySQL", "Oracle"],
                "编程语言": ["Python", "Java", "Shell"]
            },
            "证书要求": {
                "必备": [],
                "推荐": ["ISTQB", "软考中级", "CSTE"]
            },
            "软技能": {
                "抗压能力": "高",
                "沟通能力": "高",
                "学习能力": "中",
                "细心耐心": "高",
                "逻辑思维": "高"
            },
            "学历要求": {
                "最低": "本科",
                "理想": "本科"
            },
            "经验要求": {
                "初级": "1-3年",
                "中级": "3-5年",
                "高级": "5年+"
            },
            "薪资范围": {
                "初级": "7K-12K",
                "中级": "12K-18K",
                "高级": "18K-30K"
            },
            "工具技能": ["JIRA", "禅道", "Bugzilla", "Fiddler", "Charles"],
            "行业发展趋势": "AI测试、自动化测试平台、DevOps测试、质量效能"
        },
        
        "数据分析工程师": {
            "岗位名称": "数据分析工程师",
            "专业技能": {
                "编程语言": ["Python", "R", "SQL"],
                "数据分析": ["Pandas", "NumPy", "SciPy", "Excel"],
                "可视化": ["Tableau", "PowerBI", "ECharts", "Matplotlib"],
                "统计学": ["假设检验", "回归分析", "方差分析", "时间序列"],
                "机器学习": ["Scikit-learn", "XGBoost", "LightGBM"],
                "大数据": ["Hadoop", "Spark", "Hive"]
            },
            "证书要求": {
                "必备": [],
                "推荐": ["CDA", "BDA", "软考中级", "AWS数据分析师"]
            },
            "软技能": {
                "抗压能力": "中",
                "沟通能力": "高",
                "学习能力": "高",
                "业务理解": "高",
                "逻辑思维": "高"
            },
            "学历要求": {
                "最低": "本科",
                "理想": "硕士"
            },
            "经验要求": {
                "初级": "1-3年",
                "中级": "3-5年",
                "高级": "5年+"
            },
            "薪资范围": {
                "初级": "10K-18K",
                "中级": "18K-25K",
                "高级": "25K-40K"
            },
            "工具技能": ["MySQL", "Hive", "Python", "Excel", "PPT"],
            "行业发展趋势": "数据中台、BI自动化、AI数据分析、数据治理"
        },
        
        "产品经理": {
            "岗位名称": "产品经理",
            "专业技能": {
                "需求分析": ["用户调研", "需求收集", "需求分析", "PRD撰写"],
                "产品设计": ["Axure", "Sketch", "Figma", "XMind", "ProcessOn"],
                "数据分析": ["数据分析", "A/B测试", "用户留存", "漏斗分析"],
                "项目管理": ["敏捷开发", "Scrum", "瀑布模型"],
                "行业知识": ["竞品分析", "行业研究", "商业模式"]
            },
            "证书要求": {
                "必备": [],
                "推荐": ["PMP", "NPDP", "软考高级"]
            },
            "软技能": {
                "抗压能力": "高",
                "沟通能力": "高",
                "学习能力": "高",
                "创新能力": "高",
                "同理心": "高"
            },
            "学历要求": {
                "最低": "本科",
                "理想": "硕士"
            },
            "经验要求": {
                "初级": "2-3年",
                "中级": "3-5年",
                "高级": "5年+"
            },
            "薪资范围": {
                "初级": "12K-20K",
                "中级": "20K-30K",
                "高级": "30K-60K"
            },
            "工具技能": ["Axure", "XMind", "Excel", "PPT", "Notion", "飞书"],
            "行业发展趋势": "AI产品经理、数据产品经理、硬件产品经理、B端产品"
        },
        
        "UI/UX设计师": {
            "岗位名称": "UI/UX设计师",
            "专业技能": {
                "UI设计": ["界面设计", "图标设计", "品牌设计", "运营设计"],
                "UX设计": ["用户研究", "交互设计", "原型设计", "可用性测试"],
                "设计工具": ["Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator"],
                "动效设计": ["After Effects", "Principle", "Protopie"],
                "前端基础": ["HTML", "CSS", "JavaScript基础"]
            },
            "证书要求": {
                "必备": [],
                "推荐": ["Adobe认证", "UX认证", "IXDC认证"]
            },
            "软技能": {
                "抗压能力": "中",
                "沟通能力": "高",
                "学习能力": "高",
                "审美能力": "高",
                "创新能力": "高"
            },
            "学历要求": {
                "最低": "本科",
                "理想": "本科"
            },
            "经验要求": {
                "初级": "1-3年",
                "中级": "3-5年",
                "高级": "5年+"
            },
            "薪资范围": {
                "初级": "8K-15K",
                "中级": "15K-22K",
                "高级": "22K-40K"
            },
            "工具技能": ["Figma", "Sketch", "Photoshop", "Illustrator", "After Effects"],
            "行业发展趋势": "AI辅助设计、体验设计、设计系统、3D设计"
        },
        
        "网络工程师": {
            "岗位名称": "网络工程师",
            "专业技能": {
                "网络技术": ["TCP/IP", "OSI七层模型", "路由协议", "交换技术"],
                "设备配置": ["Cisco", "华为", "H3C", "Juniper"],
                "网络安全": ["防火墙", "VPN", "IDS/IPS", "加密技术"],
                "监控系统": ["Zabbix", "Nagios", "Prometheus"],
                "虚拟化": ["VMware", "KVM", "Hyper-V"],
                "脚本语言": ["Python", "Shell", "Bash"]
            },
            "证书要求": {
                "必备": [],
                "推荐": ["HCIA", "HCIP", "CCNA", "CCNP", "CISSP"]
            },
            "软技能": {
                "抗压能力": "高",
                "沟通能力": "中",
                "学习能力": "高",
                "问题解决": "高",
                "细心耐心": "高"
            },
            "学历要求": {
                "最低": "专科",
                "理想": "本科"
            },
            "经验要求": {
                "初级": "1-3年",
                "中级": "3-5年",
                "高级": "5年+"
            },
            "薪资范围": {
                "初级": "6K-10K",
                "中级": "10K-18K",
                "高级": "18K-30K"
            },
            "工具技能": ["Wireshark", "GNS3", "EVE-NG", "CRT", "Putty"],
            "行业发展趋势": "网络安全、云网络、SDN、零信任架构"
        },
        
        "运维工程师": {
            "岗位名称": "运维工程师",
            "专业技能": {
                "操作系统": ["Linux", "Windows Server", "Shell"],
                "容器技术": ["Docker", "Kubernetes", "Helm"],
                "自动化工具": ["Ansible", "SaltStack", "Puppet", "Chef"],
                "监控": ["Prometheus", "Grafana", "Zabbix", "ELK"],
                "云计算": ["AWS", "阿里云", "腾讯云", "Kubernetes"],
                "脚本语言": ["Python", "Shell", "Go"]
            },
            "证书要求": {
                "必备": [],
                "推荐": ["RHCE", "KCNA", "CKA", "软考中级"]
            },
            "软技能": {
                "抗压能力": "高",
                "沟通能力": "中",
                "学习能力": "高",
                "问题解决": "高",
                "责任心": "高"
            },
            "学历要求": {
                "最低": "本科",
                "理想": "本科"
            },
            "经验要求": {
                "初级": "1-3年",
                "中级": "3-5年",
                "高级": "5年+"
            },
            "薪资范围": {
                "初级": "8K-15K",
                "中级": "15K-22K",
                "高级": "22K-40K"
            },
            "工具技能": ["Linux", "Docker", "K8s", "Ansible", "Git", "Nginx"],
            "行业发展趋势": "SRE、DevOps、云原生运维、AIOps、GitOps"
        },
        
        "AI算法工程师": {
            "岗位名称": "AI算法工程师",
            "专业技能": {
                "编程语言": ["Python", "C++", "Java"],
                "机器学习": ["监督学习", "无监督学习", "深度学习", "强化学习"],
                "深度学习框架": ["TensorFlow", "PyTorch", "PaddlePaddle"],
                "NLP": ["Transformer", "BERT", "GPT", "文本分类", "实体识别"],
                "计算机视觉": ["图像分类", "目标检测", "图像分割", "GAN"],
                "工具": ["Git", "Docker", "Linux", "GPU编程"]
            },
            "证书要求": {
                "必备": [],
                "推荐": ["软考高级", "AWS机器学习认证", "华为AI认证", "ACM"]
            },
            "软技能": {
                "抗压能力": "高",
                "沟通能力": "中",
                "学习能力": "高",
                "创新能力": "高",
                "逻辑思维": "高"
            },
            "学历要求": {
                "最低": "硕士",
                "理想": "博士"
            },
            "经验要求": {
                "初级": "1-3年",
                "中级": "3-5年",
                "高级": "5年+"
            },
            "薪资范围": {
                "初级": "15K-25K",
                "中级": "25K-40K",
                "高级": "40K-80K"
            },
            "工具技能": ["PyTorch", "TensorFlow", "Python", "Git", "Docker", "Linux"],
            "行业发展趋势": "大语言模型、AIGC、AI Agent、多模态、边缘AI"
        }
    }
    
    @classmethod
    def get_profile(cls, job_name: str) -> Optional[Dict]:
        """获取岗位画像"""
        return cls.JOB_PROFILES.get(job_name)
    
    @classmethod
    def get_all_profiles(cls) -> Dict[str, Dict]:
        """获取所有岗位画像"""
        return cls.JOB_PROFILES
    
    @classmethod
    def generate_profile_from_llm(cls, job_description: str, llm_client) -> Dict:
        """
        使用大模型从职位描述生成画像
        
        Args:
            job_description: 职位描述文本
            llm_client: 大模型客户端实例
        
        Returns:
            结构化的岗位画像
        """
        prompt = f"""请从以下职位描述中提取关键信息，生成结构化的岗位画像JSON：

职位描述：
{job_description}

请返回以下格式的JSON（只返回JSON，不要其他内容）：
{{
    "专业技能": {{"编程语言": [], "框架": [], "工具": [], "数据库": []}},
    "证书要求": [],
    "软技能": {{"抗压能力": "", "沟通能力": "", "学习能力": ""}},
    "学历要求": "",
    "经验要求": "",
    "薪资范围": ""
}}
"""
        
        response = llm_client.call(prompt)
        
        try:
            profile = json.loads(response)
            return profile
        except json.JSONDecodeError:
            return {"error": "解析失败"}
    
    @classmethod
    def export_to_json(cls, file_path: str):
        """导出所有画像到JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cls.JOB_PROFILES, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def export_to_csv(cls, file_path: str):
        """导出所有画像到CSV文件"""
        rows = []
        
        for job_name, profile in cls.JOB_PROFILES.items():
            row = {
                '岗位名称': job_name,
                '专业技能': ','.join(sum([v if isinstance(v, list) else [] for v in profile.get('专业技能', {}).values()], [])),
                '证书要求': ','.join(profile.get('证书要求', {}).get('推荐', [])),
                '学历要求': profile.get('学历要求', {}).get('最低', ''),
                '薪资范围': profile.get('薪资范围', {}).get('中级', ''),
                '发展趋势': profile.get('行业发展趋势', '')
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')


class JobGraphBuilder:
    """岗位知识图谱构建器"""
    
    # 晋升图谱
    PROMOTION_GRAPH = {
        "Java开发工程师": [
            ["Java开发工程师", "高级Java工程师", "技术组长", "架构师", "技术总监", "CTO"],
            ["Java开发工程师", "高级Java工程师", "技术专家", "首席工程师"]
        ],
        "前端开发工程师": [
            ["前端开发工程师", "高级前端工程师", "前端组长", "前端架构师", "技术总监"]
        ],
        "软件测试工程师": [
            ["测试工程师", "高级测试工程师", "测试主管", "测试经理", "质量总监"]
        ],
        "数据分析工程师": [
            ["数据分析师", "高级数据分析师", "数据主管", "数据经理", "首席数据官"]
        ],
        "产品经理": [
            ["产品经理", "高级产品经理", "产品总监", "VP产品", "CPO"]
        ]
    }
    
    # 换岗路径图谱
    CAREER_TRANSFER_GRAPH = {
        "Java开发工程师": [
            {"from": "Java开发工程师", "to": "后端架构师", "reason": "技术深化"},
            {"from": "Java开发工程师", "to": "数据开发工程师", "reason": "数据方向"},
            {"from": "Java开发工程师", "to": "产品经理", "reason": "业务转型"},
            {"from": "Java开发工程师", "to": "AI算法工程师", "reason": "AI方向"}
        ],
        "前端开发工程师": [
            {"from": "前端开发工程师", "to": "全栈工程师", "reason": "技术扩展"},
            {"from": "前端开发工程师", "to": "UI设计师", "reason": "设计转型"},
            {"from": "前端开发工程师", "to": "产品经理", "reason": "业务发展"}
        ],
        "软件测试工程师": [
            {"from": "测试工程师", "to": "自动化测试开发", "reason": "技术提升"},
            {"from": "测试工程师", "to": "产品经理", "reason": "业务转型"},
            {"from": "测试工程师", "to": "性能测试专家", "reason": "专业深化"}
        ],
        "数据分析工程师": [
            {"from": "数据分析工程师", "to": "数据产品经理", "reason": "业务发展"},
            {"from": "数据分析工程师", "to": "AI算法工程师", "reason": "技术深化"},
            {"from": "数据分析工程师", "to": "商业分析师", "reason": "战略方向"}
        ],
        "产品经理": [
            {"from": "产品经理", "to": "产品总监", "reason": "管理发展"},
            {"from": "产品经理", "to": "项目经理", "reason": "项目管理"},
            {"from": "产品经理", "to": "运营总监", "reason": "运营发展"}
        ]
    }
    
    @classmethod
    def get_promotion_path(cls, job_name: str) -> List[List[str]]:
        """获取晋升路径"""
        return cls.PROMOTION_GRAPH.get(job_name, [])
    
    @classmethod
    def get_career_transfer_paths(cls, job_name: str) -> List[Dict]:
        """获取换岗路径"""
        return cls.CAREER_TRANSFER_GRAPH.get(job_name, [])
    
    @classmethod
    def export_graph_data(cls, format: str = 'json') -> str:
        """导出图谱数据"""
        data = {
            'promotion': cls.PROMOTION_GRAPH,
            'career_transfer': cls.CAREER_TRANSFER_GRAPH
        }
        
        if format == 'json':
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        return str(data)


# 导入pandas用于CSV导出
import pandas as pd
