"""
岗位数据处理器 - 加载和处理jobs_sample.csv数据集
"""

import pandas as pd
import json
from typing import List, Dict, Optional
import os


class JobDataProcessor:
    """岗位数据处理器"""
    
    def __init__(self, csv_path: str):
        """
        初始化数据处理器
        
        Args:
            csv_path: CSV文件路径
        """
        self.csv_path = csv_path
        self.jobs_data = None
        self.load_data()
    
    def load_data(self):
        """加载数据（支持CSV和Excel文件）"""
        try:
            if self.csv_path.endswith('.csv'):
                self.jobs_data = pd.read_csv(self.csv_path, encoding='utf-8')
            elif self.csv_path.endswith('.xls') or self.csv_path.endswith('.xlsx'):
                self.jobs_data = pd.read_excel(self.csv_path)
            else:
                raise ValueError("不支持的文件格式")
            print(f"成功加载 {len(self.jobs_data)} 条岗位数据")
            print(f"数据列名: {list(self.jobs_data.columns)}")
        except Exception as e:
            print(f"加载数据失败: {e}")
            self.jobs_data = None
    
    def _get_column_map(self) -> Dict[str, str]:
        """
        获取列名映射，处理不同数据源的列名差异
        
        Returns:
            列名映射字典
        """
        columns = list(self.jobs_data.columns)
        column_map = {
            '岗位名称': '岗位名称',
            '岗位详情': '岗位详情',
            '地址': '地址',
            '薪资范围': '薪资范围',
            '所属行业': '所属行业',
            '公司名称': '公司名称',
            '公司规模': '公司规模'
        }
        
        # 处理可能的列名变体
        for col in columns:
            col_lower = col.lower()
            if '岗位' in col_lower and '名称' in col_lower:
                column_map['岗位名称'] = col
            elif '岗位' in col_lower and ('详情' in col_lower or '描述' in col_lower):
                column_map['岗位详情'] = col
            elif '地址' in col_lower or '地点' in col_lower:
                column_map['地址'] = col
            elif '薪资' in col_lower:
                column_map['薪资范围'] = col
            elif '行业' in col_lower:
                column_map['所属行业'] = col
            elif '公司' in col_lower and '名称' in col_lower:
                column_map['公司名称'] = col
            elif '公司' in col_lower and '规模' in col_lower:
                column_map['公司规模'] = col
        
        return column_map
    
    def get_all_jobs(self) -> List[Dict]:
        """获取所有岗位数据"""
        if self.jobs_data is None:
            return []
        
        return self.jobs_data.to_dict('records')
    
    def get_jobs_by_keyword(self, keyword: str) -> List[Dict]:
        """
        根据关键词搜索岗位
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的岗位列表
        """
        if self.jobs_data is None:
            return []
        
        # 获取列名映射
        column_map = self._get_column_map()
        
        # 搜索的列
        search_columns = []
        
        # 尝试不同的列名
        possible_columns = ['岗位名称', '岗位详情', '岗位要求', '职位描述', '公司名称', '所属行业']
        for col in possible_columns:
            mapped_col = column_map.get(col, col)
            if mapped_col in self.jobs_data.columns:
                search_columns.append(mapped_col)
        
        if not search_columns:
            # 如果没有找到任何搜索列，返回空列表
            return []
        
        # 构建搜索条件
        mask = False
        for col in search_columns:
            try:
                # 尝试将列转换为字符串并搜索
                mask |= self.jobs_data[col].astype(str).str.contains(keyword, case=False, na=False)
            except Exception as e:
                # 如果转换失败，跳过该列
                pass
        
        # 返回匹配的岗位
        return self.jobs_data[mask].to_dict('records')
    
    def get_jobs_by_city(self, city: str) -> List[Dict]:
        """
        根据城市筛选岗位
        
        Args:
            city: 城市名称
            
        Returns:
            匹配的岗位列表
        """
        if self.jobs_data is None:
            return []
        
        column_map = self._get_column_map()
        address_col = column_map.get('地址', '地址')
        
        if address_col in self.jobs_data.columns:
            mask = self.jobs_data[address_col].astype(str).str.contains(city, case=False, na=False)
            return self.jobs_data[mask].to_dict('records')
        return []
    
    def get_jobs_by_industry(self, industry: str) -> List[Dict]:
        """
        根据行业筛选岗位
        
        Args:
            industry: 行业名称
            
        Returns:
            匹配的岗位列表
        """
        if self.jobs_data is None:
            return []
        
        column_map = self._get_column_map()
        industry_col = column_map.get('所属行业', '所属行业')
        
        if industry_col in self.jobs_data.columns:
            mask = self.jobs_data[industry_col].astype(str).str.contains(industry, case=False, na=False)
            return self.jobs_data[mask].to_dict('records')
        return []
    
    def get_jobs_by_salary_range(self, min_salary: float, max_salary: float) -> List[Dict]:
        """
        根据薪资范围筛选岗位
        
        Args:
            min_salary: 最低薪资（元）
            max_salary: 最高薪资（元）
            
        Returns:
            匹配的岗位列表
        """
        if self.jobs_data is None:
            return []
        
        # 解析薪资范围
        def parse_salary(salary_str):
            if pd.isna(salary_str):
                return (0, 0)
            
            # 处理不同格式的薪资
            import re
            
            # 处理小时薪资
            hour_match = re.search(r'(\d+)-(\d+)元/小时', str(salary_str))
            if hour_match:
                min_hour = float(hour_match.group(1))
                max_hour = float(hour_match.group(2))
                # 按每月160小时计算
                return (min_hour * 160, max_hour * 160)
            
            # 处理日薪资
            day_match = re.search(r'(\d+)-(\d+)元/天', str(salary_str))
            if day_match:
                min_day = float(day_match.group(1))
                max_day = float(day_match.group(2))
                # 按每月22天计算
                return (min_day * 22, max_day * 22)
            
            # 处理月薪资
            month_match = re.search(r'(\d+)-(\d+)([万千])', str(salary_str))
            if month_match:
                min_val = float(month_match.group(1))
                max_val = float(month_match.group(2))
                unit = month_match.group(3)
                
                if unit == '万':
                    return (min_val * 10000, max_val * 10000)
                elif unit == '千':
                    return (min_val * 1000, max_val * 1000)
            
            # 处理其他格式
            num_match = re.findall(r'\d+', str(salary_str))
            if num_match:
                nums = [float(num) for num in num_match]
                if len(nums) >= 2:
                    return (min(nums), max(nums))
                elif len(nums) == 1:
                    return (nums[0], nums[0])
            
            return (0, 0)
        
        # 应用薪资解析
        column_map = self._get_column_map()
        salary_col = column_map.get('薪资范围', '薪资范围')
        
        if salary_col in self.jobs_data.columns:
            self.jobs_data['min_salary'] = self.jobs_data[salary_col].apply(lambda x: parse_salary(x)[0])
            self.jobs_data['max_salary'] = self.jobs_data[salary_col].apply(lambda x: parse_salary(x)[1])
        else:
            return []
        
        # 筛选薪资范围
        mask = (self.jobs_data['min_salary'] >= min_salary) & (self.jobs_data['max_salary'] <= max_salary)
        return self.jobs_data[mask].to_dict('records')
    
    def get_industry_statistics(self) -> Dict[str, int]:
        """
        获取行业分布统计
        
        Returns:
            行业及其岗位数量
        """
        if self.jobs_data is None:
            return {}
        
        column_map = self._get_column_map()
        industry_col = column_map.get('所属行业', '所属行业')
        
        if industry_col not in self.jobs_data.columns:
            return {}
        
        # 处理行业数据，可能包含多个行业
        industry_counts = {}
        for industries in self.jobs_data[industry_col].dropna():
            for industry in str(industries).split(','):
                industry = industry.strip()
                if industry:
                    industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        return industry_counts
    
    def get_city_statistics(self) -> Dict[str, int]:
        """
        获取城市分布统计
        
        Returns:
            城市及其岗位数量
        """
        if self.jobs_data is None:
            return {}
        
        column_map = self._get_column_map()
        address_col = column_map.get('地址', '地址')
        
        if address_col not in self.jobs_data.columns:
            return {}
        
        # 提取城市信息
        city_counts = {}
        for address in self.jobs_data[address_col].dropna():
            # 提取城市名称（如：北京-海淀区 -> 北京）
            city = str(address).split('-')[0].strip()
            if city:
                city_counts[city] = city_counts.get(city, 0) + 1
        
        return city_counts
    
    def get_salary_statistics(self) -> Dict[str, float]:
        """
        获取薪资统计
        
        Returns:
            薪资统计信息
        """
        if self.jobs_data is None:
            return {}
        
        # 解析薪资
        def parse_salary(salary_str):
            if pd.isna(salary_str):
                return 0
            
            import re
            # 提取数字
            nums = re.findall(r'\d+', str(salary_str))
            if nums:
                # 取平均值
                avg = sum(float(num) for num in nums) / len(nums)
                # 处理单位
                if '万' in str(salary_str):
                    return avg * 10000
                elif '千' in str(salary_str):
                    return avg * 1000
            return 0
        
        column_map = self._get_column_map()
        salary_col = column_map.get('薪资范围', '薪资范围')
        
        if salary_col not in self.jobs_data.columns:
            return {}
        
        self.jobs_data['avg_salary'] = self.jobs_data[salary_col].apply(parse_salary)
        
        return {
            'average': float(self.jobs_data['avg_salary'].mean()),
            'median': float(self.jobs_data['avg_salary'].median()),
            'max': float(self.jobs_data['avg_salary'].max()),
            'min': float(self.jobs_data['avg_salary'].min())
        }
    
    def export_to_json(self, output_path: str):
        """
        导出数据到JSON文件
        
        Args:
            output_path: 输出文件路径
        """
        if self.jobs_data is None:
            return
        
        data = self.jobs_data.to_dict('records')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已导出到 {output_path}")
    
    def get_recommended_jobs(self, skills: List[str], experience: str = "", education: str = "", city: str = "", job_types: List[str] = None) -> List[Dict]:
        """
        根据用户技能和求职意向推荐岗位
        
        Args:
            skills: 用户技能列表
            experience: 工作经验
            education: 学历
            city: 期望城市
            job_types: 期望岗位类型列表
            
        Returns:
            推荐的岗位列表
        """
        if self.jobs_data is None:
            return []
        
        # 获取列名映射
        column_map = self._get_column_map()
        job_title_col = column_map.get('岗位名称', '岗位名称')
        job_detail_col = column_map.get('岗位详情', '岗位详情')
        address_col = column_map.get('地址', '地址')
        
        # 计算匹配度
        def calculate_match(job):
            # 获取岗位信息
            job_title = str(job.get(job_title_col, ''))
            job_detail = str(job.get(job_detail_col, ''))
            job_address = str(job.get(address_col, ''))
            
            job_desc = job_detail + ' ' + job_title
            match_score = 0
            
            # 技能匹配
            for skill in skills:
                if skill.lower() in job_desc.lower():
                    match_score += 10
            
            # 经验匹配
            if experience:
                if experience in job_detail:
                    match_score += 5
            
            # 学历匹配
            if education:
                if education in job_detail:
                    match_score += 3
            
            # 城市匹配
            if city:
                if city in job_address:
                    match_score += 15  # 城市匹配权重较高
            
            # 岗位类型匹配
            if job_types:
                for job_type in job_types:
                    if job_type in job_title:
                        match_score += 12  # 岗位类型匹配权重较高
            
            return match_score
        
        # 计算所有岗位的匹配度
        self.jobs_data['match_score'] = self.jobs_data.apply(calculate_match, axis=1)
        
        # 按匹配度排序
        sorted_jobs = self.jobs_data.sort_values('match_score', ascending=False)
        
        # 返回前10个匹配度最高的岗位
        return sorted_jobs.head(10).to_dict('records')


# 测试代码
if __name__ == "__main__":
    processor = JobDataProcessor('data/jobs_sample.csv')
    
    # 测试获取所有岗位
    print(f"总岗位数: {len(processor.get_all_jobs())}")
    
    # 测试关键词搜索
    java_jobs = processor.get_jobs_by_keyword('Java')
    print(f"Java相关岗位: {len(java_jobs)}")
    
    # 测试城市筛选
    beijing_jobs = processor.get_jobs_by_city('北京')
    print(f"北京岗位: {len(beijing_jobs)}")
    
    # 测试行业统计
    industry_stats = processor.get_industry_statistics()
    print("行业分布:", industry_stats)
    
    # 测试薪资统计
    salary_stats = processor.get_salary_statistics()
    print("薪资统计:", salary_stats)
    
    # 测试推荐功能
    recommended = processor.get_recommended_jobs(['Java', 'SpringBoot', 'MySQL'])
    print(f"推荐岗位数: {len(recommended)}")
    for job in recommended[:3]:
        print(f"推荐岗位: {job['岗位名称']}, 薪资: {job['薪资范围']}")
