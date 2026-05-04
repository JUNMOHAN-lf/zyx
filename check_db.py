import sqlite3

# 连接数据库
conn = sqlite3.connect('./data/career_planner.db')
c = conn.cursor()

# 查询career_reports表中的数据
print('=== career_reports表数据 ===')
print('ID\tUsername\tCreated At')
print('-' * 50)

c.execute('SELECT id, username, created_at FROM career_reports ORDER BY created_at DESC LIMIT 10')
for row in c.fetchall():
    print(f'{row[0]}\t{row[1]}\t{row[2]}')

# 检查表结构
print('\n=== 表结构 ===')
c.execute('PRAGMA table_info(career_reports)')
print('Field\tType\tNotNull\tDefault')
print('-' * 60)
for row in c.fetchall():
    print(f'{row[1]}\t{row[2]}\t{row[3]}\t{row[4]}')

# 检查系统时间
import datetime
print('\n=== 系统当前时间 ===')
print(datetime.datetime.now())

conn.close()
