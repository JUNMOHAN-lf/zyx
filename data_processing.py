"""
数据处理模块 - 岗位数据清洗与预处理
"""

import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple
import json


class JobDataProcessor:
    """岗位数据处理器"""
    
    def __init__(self):
        self.raw_data = None
        self.cleaned_data = None
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """加载数据"""
        if file_path.endswith('.csv'):
            self.raw_data = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            self.raw_data = pd.read_excel(file_path)
        else:
            raise ValueError("不支持的文件格式")
        
        return self.raw_data
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清洗"""
        df = df.copy()
        
        # 1. 删除重复行
        df = df.drop_duplicates()
        
        # 2. 删除职位描述为空的行
        if '职位描述' in df.columns:
            df = df[df['职位描述'].notna() & (df['职位描述'] != '')]
        
        # 3. 统一薪资格式
        if '薪资' in df.columns:
            df['薪资'] = df['薪资'].apply(self._normalize_salary)
        
        # 4. 统一城市格式
        if '城市' in df.columns:
            df['城市'] = df['城市'].apply(self._normalize_city)
        
        # 5. 统一行业格式
        if '行业' in df.columns:
            df['行业'] = df['行业'].apply(self._normalize_industry)
        
        self.cleaned_data = df
        return df
    
    def _normalize_salary(self, salary: str) -> str:
        """标准化薪资格式"""
        if pd.isna(salary):
            return "面议"
        
        salary = str(salary)
        
        # 提取数字
        numbers = re.findall(r'\d+', salary)
        if numbers:
            if '千' in salary:
                return f"{numbers[0]}K"
            elif '万' in salary:
                if len(numbers) >= 2:
                    return f"{numbers[0]}-{numbers[1]}K"
                return f"{numbers[0]}K"
        
        return salary
    
    def _normalize_city(self, city: str) -> str:
        """标准化城市"""
        if pd.isna(city):
            return "未知"
        
        city_map = {
            '北京': '北京',
            '上海': '上海', 
            '深圳': '深圳',
            '广州': '广州',
            '杭州': '杭州',
            '南京': '南京',
            '成都': '成都',
            '武汉': '武汉',
            '西安': '西安',
            '苏州': '苏州'
        }
        
        for key, value in city_map.items():
            if key in str(city):
                return value
        
        return str(city)[:4]
    
    def _normalize_industry(self, industry: str) -> str:
        """标准化行业"""
        if pd.isna(industry):
            return "互联网"
        
        industry_map = {
            '互联网': '互联网',
            '软件': '互联网',
            '电商': '电子商务',
            '金融': '金融',
            '银行': '金融',
            '教育': '教育培训',
            '房地产': '房地产',
            '制造': '制造业'
        }
        
        for key, value in industry_map.items():
            if key in str(industry):
                return value
        
        return "其他"
    
    def filter_it_jobs(self, df: pd.DataFrame) -> pd.DataFrame:
        """筛选IT/互联网类岗位"""
        it_keywords = [
            'java', 'python', '前端', '后端', '测试', '开发', 
            '算法', '数据', '产品', '设计', '运维', '安全',
            '软件', '网络', '云', 'AI', '人工智能', '机器学习'
        ]
        
        # 根据职位名称或职位描述筛选
        mask = df['职位名称'].str.lower().apply(
            lambda x: any(kw in str(x).lower() for kw in it_keywords)
        ) if '职位名称' in df.columns else False
        
        return df[mask]
    
    def cluster_jobs(self, df: pd.DataFrame) -> Dict[str, List]:
        """按岗位名称聚类"""
        clusters = {}
        
        # 定义岗位分类关键词
        job_categories = {
            'Java开发工程师': ['java', '后端', '服务端'],
            '前端开发工程师': ['前端', 'web', 'html', 'css', 'javascript', 'vue', 'react'],
            'Python开发工程师': ['python', '爬虫', 'django', 'flask'],
            '软件测试工程师': ['测试', 'qa', 'test'],
            '数据分析工程师': ['数据分析', '数据分析师', 'bi', '大数据'],
            '产品经理': ['产品经理', '产品', 'product'],
            'UI/UX设计师': ['设计', 'ui', 'ux', '美工'],
            '网络工程师': ['网络', '运维', '安全', 'h3c', 'cisco'],
            '运维工程师': ['运维', 'dba', '数据库'],
            'AI算法工程师': ['算法', 'ai', '人工智能', '机器学习', '深度学习', 'nlp']
        }
        
        for category, keywords in job_categories.items():
            mask = df['职位名称'].str.lower().apply(
                lambda x: any(kw in str(x).lower() for kw in keywords)
            )
            clusters[category] = df[mask].to_dict('records')
        
        return clusters
    
    def generate_statistics(self, df: pd.DataFrame) -> Dict:
        """生成数据统计"""
        stats = {
            '总岗位数': len(df),
            '公司数量': df['公司'].nunique() if '公司' in df.columns else 0,
            '城市分布': df['城市'].value_counts().head(10).to_dict() if '城市' in df.columns else {},
            '行业分布': df['行业'].value_counts().head(10).to_dict() if '行业' in df.columns else {},
            '薪资分布': df['薪资'].value_counts().head(10).to_dict() if '薪资' in df.columns else {}
        }
        
        return stats


def process_job_data(input_file: str, output_file: str = None) -> Dict:
    """
    完整的数据处理流程
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
    
    Returns:
        处理后的数据和统计信息
    """
    processor = JobDataProcessor()
    
    # 1. 加载数据
    df = processor.load_data(input_file)
    
    # 2. 清洗数据
    df = processor.clean_data(df)
    
    # 3. 筛选IT岗位
    df = processor.filter_it_jobs(df)
    
    # 4. 聚类
    clusters = processor.cluster_jobs(df)
    
    # 5. 统计
    stats = processor.generate_statistics(df)
    
    # 保存结果
    if output_file:
        if output_file.endswith('.csv'):
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
        elif output_file.endswith('.xlsx'):
            df.to_excel(output_file, index=False)
    
    return {
        'data': df,
        'clusters': clusters,
        'statistics': stats
    }


if __name__ == "__main__":
    # 示例用法
    result = process_job_data("jobs.csv", "jobs_cleaned.csv")
    print(f"处理完成: {result['statistics']}")
