"""
知识图谱可视化模块 - 使用Pyvis生成交互式图谱
"""

import json
import networkx as nx
from pyvis.network import Network
import tempfile
import os
from typing import List, Dict, Optional


class CareerGraphVisualizer:
    """职业发展图谱可视化"""
    
    def __init__(self):
        self.net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
        self.net.barnes_hut()
    
    def create_promotion_graph(self, job_name: str, paths: List[List[str]]) -> str:
        """
        创建晋升路径图谱
        
        Args:
            job_name: 岗位名称
            paths: 晋升路径列表
        
        Returns:
            HTML字符串
        """
        # 清空网络
        self.net = Network(height="600px", width="100%", bgcolor="#1a1a2e", font_color="white")
        self.net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=150)
        
        # 添加节点和边
        all_nodes = []
        for path in paths:
            all_nodes.extend(path)
        
        # 去重
        all_nodes = list(dict.fromkeys(all_nodes))
        
        # 添加节点
        for i, node in enumerate(all_nodes):
            # 根据层级设置颜色
            level = 0
            for path in paths:
                if node in path:
                    level = path.index(node)
                    break
            
            if level == 0:
                color = "#4CAF50"  # 绿色 - 起点
            elif level == len(paths[0]) - 1:
                color = "#F44336"  # 红色 - 终点
            else:
                color = "#2196F3"  # 蓝色 - 中间
            
            self.net.add_node(i, label=node, title=node, color=color, size=30)
        
        # 添加边
        for path in paths:
            for i in range(len(path) - 1):
                from_node = all_nodes.index(path[i])
                to_node = all_nodes.index(path[i + 1])
                self.net.add_edge(from_node, to_node, color="#888888")
        
        # 保存为HTML
        return self.net.save_graph("promotion_graph.html")
    
    def create_career_transfer_graph(self, job_name: str, paths: List[Dict]) -> str:
        """
        创建换岗路径图谱
        
        Args:
            job_name: 起始岗位
            paths: 换岗路径列表
        
        Returns:
            HTML字符串
        """
        self.net = Network(height="600px", width="100%", bgcolor="#1a1a2e", font_color="white")
        self.net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=200)
        
        # 添加起始节点
        start_node = job_name
        self.net.add_node(start_node, label=start_node, title=start_node, 
                         color="#667eea", size=40)
        
        # 添加目标节点和边
        for i, path in enumerate(paths):
            to_node = path.get("to", "")
            reason = path.get("reason", "")
            
            if to_node:
                self.net.add_node(to_node, label=to_node, title=f"{to_node}\n原因: {reason}",
                                 color="#27ae60", size=25)
                self.net.add_edge(start_node, to_node, 
                                 title=reason, color="#888888",
                                 arrows="to")
        
        return self.net.save_graph("career_transfer.html")
    
    def create_full_career_map(self, all_jobs: Dict[str, List], 
                               promotion_paths: Dict, 
                               career_paths: Dict) -> str:
        """
        创建完整的职业发展地图
        
        Args:
            all_jobs: 所有岗位信息
            promotion_paths: 晋升路径
            career_paths: 换岗路径
        
        Returns:
            HTML字符串
        """
        self.net = Network(height="800px", width="100%", bgcolor="#1a1a2e", font_color="white")
        self.net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=180)
        
        # 岗位分类颜色
        job_colors = {
            "开发": "#667eea",
            "测试": "#27ae60",
            "产品": "#f39c12",
            "设计": "#e74c3c",
            "数据": "#3498db",
            "运维": "#9b59b6",
            "AI": "#1abc9c"
        }
        
        # 添加所有岗位节点
        for job in all_jobs.keys():
            # 确定颜色
            color = "#95a5a6"
            for category, c in job_colors.items():
                if category in job:
                    color = c
                    break
            
            self.net.add_node(job, label=job, title=job, color=color, size=25)
        
        # 添加晋升路径边
        for job, paths in promotion_paths.items():
            for path in paths:
                levels = path.split(" → ")
                for i in range(len(levels) - 1):
                    try:
                        self.net.add_edge(levels[i], levels[i+1], 
                                         color="#4CAF50", width=2, arrows="to")
                    except:
                        pass
        
        # 添加换岗路径边
        for job, paths in career_paths.items():
            for path in paths:
                try:
                    self.net.add_edge(path["from"], path["to"], 
                                     color="#f39c12", width=1.5, 
                                     arrows="to", dashes=True)
                except:
                    pass
        
        return self.net.save_graph("full_career_map.html")
    
    def generate_networkx_graph(self, paths: List[List[str]]) -> nx.DiGraph:
        """
        生成NetworkX有向图（用于分析）
        """
        G = nx.DiGraph()
        
        for path in paths:
            # 添加路径上的所有节点和边
            for i in range(len(path) - 1):
                G.add_edge(path[i], path[i+1])
        
        return G
    
    def find_shortest_path(self, graph: nx.DiGraph, 
                         start: str, end: str) -> Optional[List[str]]:
        """
        查找最短路径
        """
        try:
            return nx.shortest_path(graph, start, end)
        except nx.NetworkXNoPath:
            return None
    
    def find_all_reachable(self, graph: nx.DiGraph, start: str) -> List[str]:
        """
        查找从某节点可达的所有节点
        """
        try:
            return list(nx.descendants(graph, start))
        except:
            return []


class GraphExporter:
    """图谱导出器"""
    
    @staticmethod
    def to_json(data: Dict, file_path: str):
        """导出为JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def to_gexf(graph: nx.DiGraph, file_path: str):
        """导出为GEXF格式（可用于Gephi）"""
        nx.write_gexf(graph, file_path)
    
    @staticmethod
    def to_dot(graph: nx.DiGraph, file_path: str):
        """导出为DOT格式（可用于Graphviz）"""
        nx.drawing.nx_pydot.write_dot(graph, file_path)


def generate_graph_html(job_name: str, job_data: dict) -> str:
    """
    生成岗位图谱HTML的便捷函数
    """
    visualizer = CareerGraphVisualizer()
    
    # 获取晋升路径
    from job_profiles import JobGraphBuilder
    promotion_paths = JobGraphBuilder.get_promotion_path(job_name)
    career_paths = JobGraphBuilder.get_career_transfer_paths(job_name)
    
    # 格式化晋升路径
    formatted_promotion = []
    for path in promotion_paths:
        formatted_promotion.append(path.split(" → "))
    
    # 生成晋升图谱
    if formatted_promotion:
        return visualizer.create_promotion_graph(job_name, formatted_promotion)
    
    return ""


if __name__ == "__main__":
    # 测试代码
    visualizer = CareerGraphVisualizer()
    
    # 测试晋升路径
    paths = [
        ["Java开发工程师", "高级Java工程师", "技术组长", "架构师", "技术总监"],
        ["Java开发工程师", "高级Java工程师", "技术专家", "首席工程师"]
    ]
    
    html = visualizer.create_promotion_graph("Java开发工程师", paths)
    print("晋升图谱已生成")
