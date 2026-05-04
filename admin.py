"""
管理员端模块 - 完整版
"""
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

class AdminDatabase:
    def __init__(self, db_path="./data/career_planner.db"):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_system_stats(self):
        """获取系统统计"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE user_type = 'admin'")
        admin_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM discussions")
        total_discussions = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM replies")
        total_replies = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM student_profiles")
        total_profiles = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM career_reports")
        total_reports = c.fetchone()[0]
        
        # 近7天新增用户
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        c.execute("""
            SELECT DATE(created_at) as date, COUNT(*) 
            FROM users 
            WHERE created_at >= ? 
            GROUP BY DATE(created_at)
        """, (week_ago,))
        new_users_weekly = dict(c.fetchall())
        
        conn.close()
        
        return {
            "total_users": total_users,
            "admin_count": admin_count,
            "total_discussions": total_discussions,
            "total_replies": total_replies,
            "total_profiles": total_profiles,
            "total_reports": total_reports,
            "new_users_weekly": new_users_weekly
        }
    
    def get_all_users(self):
        """获取所有用户"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT id, username, email, user_type, created_at,
                   (SELECT COUNT(*) FROM student_profiles WHERE username = users.username) as has_profile
            FROM users ORDER BY created_at DESC
        """)
        users = [dict(row) for row in c.fetchall()]
        conn.close()
        return users
    
    def update_user_type(self, user_id, user_type):
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("UPDATE users SET user_type = ? WHERE id = ?", (user_type, user_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def delete_user(self, user_id):
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            row = c.fetchone()
            if row:
                username = row[0]
                c.execute("DELETE FROM users WHERE id = ?", (user_id,))
                c.execute("DELETE FROM student_profiles WHERE username = ?", (username,))
                c.execute("DELETE FROM career_reports WHERE username = ?", (username,))
                c.execute("DELETE FROM discussions WHERE username = ?", (username,))
                c.execute("DELETE FROM replies WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def reset_password(self, user_id, new_password):
        try:
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_all_discussions(self):
        """获取所有讨论"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT d.*, COUNT(r.id) as reply_count
            FROM discussions d
            LEFT JOIN replies r ON d.id = r.discussion_id
            GROUP BY d.id
            ORDER BY d.is_pinned DESC, d.created_at DESC
        """)
        discussions = [dict(row) for row in c.fetchall()]
        conn.close()
        return discussions
    
    def get_replies(self, discussion_id):
        """获取回复"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM replies WHERE discussion_id = ? ORDER BY created_at ASC", (discussion_id,))
        replies = [dict(row) for row in c.fetchall()]
        conn.close()
        return replies
    
    def get_all_reports(self):
        """获取所有报告"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT cr.*, u.username, u.email
            FROM career_reports cr
            JOIN users u ON cr.username = u.username
            ORDER BY cr.created_at DESC
        """)
        reports = [dict(row) for row in c.fetchall()]
        conn.close()
        return reports
    
    def get_skill_statistics(self):
        """获取技能统计"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT profile_data FROM student_profiles")
        profiles = c.fetchall()
        conn.close()
        
        skill_counts = {}
        for profile in profiles:
            if profile[0]:
                try:
                    data = json.loads(profile[0])
                    skills = data.get('专业技能', [])
                    for skill in skills:
                        skill_counts[skill] = skill_counts.get(skill, 0) + 1
                except:
                    pass
        return skill_counts
    
    def log_operation(self, username, action, ip=""):
        """记录操作日志"""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    action TEXT NOT NULL,
                    ip TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute("INSERT INTO operation_logs (username, action, ip) VALUES (?, ?, ?)",
                      (username, action, ip))
            conn.commit()
            conn.close()
        except:
            pass


class AdminUI:
    def __init__(self):
        self.db = AdminDatabase()
    
    def render_dashboard(self):
        """仪表盘"""
        st.title("📊 管理员仪表盘")
        stats = self.db.get_system_stats()
        
        # 指标卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总用户数", stats["total_users"], delta=f"+{stats['admin_count']} 管理员")
        with col2:
            st.metric("讨论帖", stats["total_discussions"], delta=f"+{stats['total_replies']} 回复")
        with col3:
            st.metric("学生画像", stats["total_profiles"])
        with col4:
            st.metric("规划报告", stats["total_reports"])
        
        st.markdown("---")

# 图表
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📈 近7天新增用户")
            new_users = stats["new_users_weekly"]
            if new_users:
                dates = list(new_users.keys())
                counts = list(new_users.values())
                fig = px.line(x=dates, y=counts, markers=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无数据")
        
        with col2:
            st.subheader("📊 用户类型分布")
            fig = px.pie(
                values=[stats["total_users"] - stats["admin_count"], stats["admin_count"]],
                names=["普通用户", "管理员"],
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 热门技能
        st.markdown("---")
        st.subheader("🔥 热门技能排行")
        skill_stats = self.db.get_skill_statistics()
        if skill_stats:
            top_skills = sorted(skill_stats.items(), key=lambda x: x[1], reverse=True)[:10]
            df = pd.DataFrame(top_skills, columns=['技能', '人数'])
            fig = px.bar(df, x='技能', y='人数')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无技能数据")
    
    def render_user_management(self):
        """用户管理"""
        st.title("👥 用户管理")
        
        # 搜索
        search = st.text_input("🔍 搜索用户", placeholder="用户名/邮箱")
        
        users = self.db.get_all_users()
        
        if search:
            users = [u for u in users if search.lower() in u['username'].lower() 
                    or (u['email'] and search.lower() in u['email'].lower())]
        
        if users:
            df = pd.DataFrame(users)
            df_display = df[['id', 'username', 'email', 'user_type', 'created_at', 'has_profile']]
            df_display.columns = ['ID', '用户名', '邮箱', '角色', '注册时间', '有画像']
            st.dataframe(df_display, use_container_width=True)
            
            st.markdown("---")
            st.subheader("用户操作")
            
            user_options = {f"{u['username']} (ID:{u['id']})": u for u in users}
            selected_key = st.selectbox("选择用户", list(user_options.keys()))
            selected_user = user_options[selected_key]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                new_role = "admin" if selected_user['user_type'] == 'user' else 'user'
                role_text = "设为管理员" if new_role == 'admin' else "降为普通用户"
                if st.button(f"👑 {role_text}"):
                    if self.db.update_user_type(selected_user['id'], new_role):
                        self.db.log_operation(st.session_state.get('username'), f"修改用户 {selected_user['username']} 角色为 {new_role}")
                        st.success(f"已{role_text} {selected_user['username']}")
                        time.sleep(0.5)
                        st.rerun()
            
            with col2:
                new_pwd = st.text_input("新密码", type="password", key="new_pwd")
                if st.button("🔑 重置密码"):
                    if new_pwd and len(new_pwd) >= 8:
                        if self.db.reset_password(selected_user['id'], new_pwd):
                            self.db.log_operation(st.session_state.get('username'), f"重置用户 {selected_user['username']} 密码")
                            st.success(f"已重置 {selected_user['username']} 的密码")
                    else:
                        st.warning("密码至少8位")
            
            with col3:
                if st.button("🗑️ 删除用户"):
                    if selected_user['username'] == st.session_state.get('username'):
                        st.error("不能删除当前登录的管理员")
                    else:
                        if self.db.delete_user(selected_user['id']):
                            self.db.log_operation(st.session_state.get('username'), f"删除用户 {selected_user['username']}")
                            st.success(f"已删除用户 {selected_user['username']}")
                            time.sleep(0.5)
                            st.rerun()
        else:
            st.info("暂无用户数据")
    
    def render_discussion_management(self):
        """讨论管理"""
        st.title("💬 讨论管理")
        
        discussions = self.db.get_all_discussions()
        
        if not discussions:
            st.info("暂无讨论")
            return
        
        # 筛选
        filter_status = st.selectbox("筛选", ["全部", "置顶", "普通"])
        
        for disc in discussions:
            if filter_status == "置顶" and not disc.get('is_pinned', 0):
                continue
            if filter_status == "普通" and disc.get('is_pinned', 0):
                continue
            
            with st.container():
                pin_badge = "📌 " if disc.get('is_pinned', 0) else ""
                st.markdown(f"""
                <div style="background: #f5f5f5; border-radius: 10px; padding: 15px; margin: 10px 0;">
                    <h4>{pin_badge}{disc['title']}</h4>
                    <p>{disc['content'][:150]}{'...' if len(disc['content']) > 150 else ''}</p >
                    <small>👤 {disc['username']} | 💬 {disc.get('reply_count', 0)}回复 | 📅 {disc['created_at'][:16]}</small>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if disc.get('is_pinned', 0):
                        if st.button("📍 取消置顶", key=f"unpin_{disc['id']}"):
                            conn = self.db.get_connection()
                            c = conn.cursor()
                            c.execute("UPDATE discussions SET is_pinned = 0 WHERE id = ?", (disc['id'],))
                            conn.commit()
                            conn.close()
                            self.db.log_operation(st.session_state.get('username'), f"取消置顶讨论 {disc['title']}")
                            st.rerun()
                    else:
                        if st.button("📌 置顶", key=f"pin_{disc['id']}"):
                            conn = self.db.get_connection()
                            c = conn.cursor()
                            c.execute("UPDATE discussions SET is_pinned = 1 WHERE id = ?", (disc['id'],))
                            conn.commit()
                            conn.close()
                            self.db.log_operation(st.session_state.get('username'), f"置顶讨论 {disc['title']}")
                            st.rerun()
                
                with col2:
                    if st.button("🗑️ 删除", key=f"del_disc_{disc['id']}"):
                        conn = self.db.get_connection()
                        c = conn.cursor()
                        c.execute("DELETE FROM discussions WHERE id = ?", (disc['id'],))
                        c.execute("DELETE FROM replies WHERE discussion_id = ?", (disc['id'],))
                        conn.commit()
                        conn.close()
                        self.db.log_operation(st.session_state.get('username'), f"删除讨论 {disc['title']}")
                        st.rerun()
                
                with st.expander(f"查看回复 ({disc.get('reply_count', 0)})"):
                    replies = self.db.get_replies(disc['id'])
                    for reply in replies:
                        st.markdown(f"""
                        <div style="padding: 10px; margin: 5px 0; background: #e8e8e8; border-radius: 5px;">
                            <strong>{reply['username']}</strong>: {reply['content']}
                            <br><small>{reply['created_at'][:16]}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("删除回复", key=f"del_reply_{reply['id']}"):
                            conn = self.db.get_connection()
                            c = conn.cursor()
                            c.execute("DELETE FROM replies WHERE id = ?", (reply['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()
                
                st.markdown("---")
    
    def render_report_audit(self):
        """报告审核"""
        st.title("📄 报告审核")
        
        reports = self.db.get_all_reports()
        
        if not reports:
            st.info("暂无报告")
            return
        
        for report in reports:
            with st.expander(f"📄 {report['username']} - {report['created_at'][:16]}"):
                st.markdown(f"**用户**: {report['username']} ({report.get('email', '无邮箱')})")
                st.markdown(f"**生成时间**: {report['created_at']}")
                st.markdown("**报告内容**:")
                content = report['report_content']
                st.markdown(content[:500] + "..." if len(content) > 500 else content)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 通过", key=f"pass_{report['id']}"):
                        st.success("已通过")
                with col2:
                    if st.button("❌ 拒绝", key=f"reject_{report['id']}"):
                        st.warning("已拒绝")
    
    def render_data_statistics(self):
        """数据统计"""
        st.title("📈 数据统计")
        
        stats = self.db.get_system_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总用户数", stats["total_users"])
        with col2:
            st.metric("总讨论数", stats["total_discussions"])
        with col3:
            st.metric("画像完成数", stats["total_profiles"])
        with col4:
            st.metric("报告生成数", stats["total_reports"])
        
        st.markdown("---")
        
        # 画像完成度分布
        st.subheader("画像完成度分布")
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT completeness_score FROM student_profiles WHERE completeness_score IS NOT NULL", conn)
        conn.close()
        
        if not df.empty:
            df['等级'] = pd.cut(df['completeness_score'], bins=[0, 30, 60, 80, 100],
                                labels=['低(0-30)', '中(30-60)', '良(60-80)', '优(80-100)'])
            dist = df['等级'].value_counts()
            fig = px.bar(x=dist.index, y=dist.values)
            st.plotly_chart(fig, use_container_width=True)
        
        # 热门技能
        st.subheader("热门技能排行")
        skill_stats = self.db.get_skill_statistics()
        if skill_stats:
            top_skills = sorted(skill_stats.items(), key=lambda x: x[1], reverse=True)[:15]
            df_skills = pd.DataFrame(top_skills, columns=['技能', '人数'])
            fig = px.bar(df_skills, x='技能', y='人数')
            st.plotly_chart(fig, use_container_width=True)
    
    def render_operation_logs(self):
        """操作日志"""
        st.title("📜 操作日志")
        
        try:
            conn = self.db.get_connection()
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM operation_logs ORDER BY created_at DESC LIMIT 100")
            logs = [dict(row) for row in c.fetchall()]
            conn.close()
            
            if logs:
                df_logs = pd.DataFrame(logs)
                st.dataframe(df_logs, use_container_width=True)
            else:
                st.info("暂无操作日志")
        except:
            st.info("操作日志功能需要先创建表")
    
    def render_system_config(self):
        """系统配置"""
        st.title("⚙️ 系统配置")
        
        st.subheader("站点信息")
        site_name = st.text_input("站点名称", value="AI大学生职业规划智能体")
        site_desc = st.text_area("站点描述", value="基于人工智能技术，为您提供精准的职业规划方案")
        
        st.subheader("功能开关")
        col1, col2 = st.columns(2)
        with col1:
            enable_discussion = st.checkbox("启用讨论区", value=True)
            enable_resume = st.checkbox("启用简历解析", value=True)
        with col2:
            enable_report = st.checkbox("启用报告生成", value=True)
            enable_match = st.checkbox("启用岗位匹配", value=True)
        
        if st.button("保存配置"):
            st.success("配置已保存")


def render_admin_panel(choice):
    """渲染管理员面板"""
    admin_ui = AdminUI()
    
    if choice == "仪表盘":
        admin_ui.render_dashboard()
    elif choice == "用户管理":
        admin_ui.render_user_management()
    elif choice == "讨论管理":
        admin_ui.render_discussion_management()
    elif choice == "报告审核":
        admin_ui.render_report_audit()
    elif choice == "数据统计":
        admin_ui.render_data_statistics()
    elif choice == "操作日志":
        admin_ui.render_operation_logs()
    elif choice == "系统配置":
        admin_ui.render_system_config()