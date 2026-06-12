import openpyxl
import os

# 打开 Excel 文件
wb = openpyxl.load_workbook('SoupData.xlsx')
sheet = wb.active

lines = []
# 从第二行开始读（跳过第一行的表头）
for row in sheet.iter_rows(min_row=2, values_only=True):
    if not row[0]: # 如果标题是空的，说明读到底了，跳出
        continue

    # 提取四列数据，如果没有填则默认为空字符串或"中等"
    title = str(row[0] or "")
    question = str(row[1] or "")
    answer = str(row[2] or "")
    difficulty = str(row[3] or "中等")

    # 施展魔法：把 Excel 里的真实换行，替换为程序需要的 \n
    question = question.replace('\n', '\\n').replace('\r', '')
    answer = answer.replace('\n', '\\n').replace('\r', '')

    # 拼接成竖线格式
    line = f"{title}|{question}|{answer}|{difficulty}"
    lines.append(line)

# 生成 TXT 文件并保存为 UTF-8 编码
with open('SoupDatabase.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
