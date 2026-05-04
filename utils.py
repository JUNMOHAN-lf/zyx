"""
工具函数模块
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed

def calculate_completeness_score(profile: Dict) -> float:
    """计算画像完整度"""
    score = 0
    basic = profile.get("基本信息", {})
    if basic.get("姓名"): score += 5
    if basic.get("专业"): score += 5
    if basic.get("学历"): score += 5
    if basic.get("学校"): score += 5
    
    skills = profile.get("专业技能", [])
    score += min(30, len(skills) * 6)
    
    certs = profile.get("证书", [])
    score += min(20, len(certs) * 5)
    
    projects = profile.get("项目经验", [])
    score += min(20, len(projects) * 7)
    
    if profile.get("实习经历"):
        score += 10
    
    return min(100, score)

def calculate_competitiveness_score(profile: Dict) -> float:
    """计算竞争力评分"""
    score = 0
    skills = profile.get("专业技能", [])
    skill_weight = {
        "Python": 10, "Java": 10, "机器学习": 15, "深度学习": 15,
        "云原生": 12, "Docker": 8, "K8s": 10, "大数据": 10
    }
    for skill in skills:
        score += skill_weight.get(skill, 2)
    
    certs = profile.get("证书", [])
    cert_weight = {"软考高级": 15, "软考中级": 10, "PMP": 10}
    for cert in certs:
        score += cert_weight.get(cert, 2)
    
    projects = profile.get("项目经验", [])
    score += min(30, len(projects) * 10)
    
    return min(100, score)

def get_skill_categories() -> Dict:
    """获取技能分类"""
    return {
        "编程语言": ["Python", "Java", "JavaScript", "C++", "Go", "Rust"],
        "前端技术": ["HTML", "CSS", "Vue", "React", "Angular"],
        "后端框架": ["SpringBoot", "Django", "Flask", "FastAPI"],
        "数据库": ["MySQL", "PostgreSQL", "MongoDB", "Redis"],
        "云技术": ["Docker", "Kubernetes", "AWS", "阿里云"],
        "AI/ML": ["TensorFlow", "PyTorch", "机器学习", "深度学习"]
    }

def get_certificate_categories() -> Dict:
    """获取证书分类"""
    return {
        "技术认证": ["软考初级", "软考中级", "软考高级", "AWS认证"],
        "专业资格": ["PMP", "NPDP", "CISSP"],
        "语言证书": ["英语四级", "英语六级", "雅思", "托福"]
    }