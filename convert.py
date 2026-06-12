import openpyxl
import os

# 打开 Excel 文件
wb = openpyxl.load_workbook('海龟汤_问卷_SoupData.xlsx')
sheet = wb.active

# 🌟 智能升级：读取第一行表头，自动寻找四大数据在哪一列！
header_row = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]

title_idx = -1
question_idx = -1
answer_idx = -1
diff_idx = -1

for i, col_name in enumerate(header_row):
    # 只要表头里包含这些关键字，就自动认领这一列
    if "标题" in col_name or "名字" in col_name or "名称" in col_name:
        title_idx = i
    elif "汤面" in col_name:
        question_idx = i
    elif "汤底" in col_name:
        answer_idx = i
    elif "难度" in col_name:
        diff_idx = i

# 防呆：如果问卷表头写得太奇怪没识别出来，就按原来默认的ABCD列兜底
if title_idx == -1: title_idx = 0
if question_idx == -1: question_idx = 1
if answer_idx == -1: answer_idx = 2
if diff_idx == -1: diff_idx = 3

lines = []
# 从第二行开始读数据
for row in sheet.iter_rows(min_row=2, values_only=True):
    # 如果这行的标题列是空的，说明读到底了，跳过
    if not row[title_idx]: 
        continue

    # 根据刚才找到的列索引，精准提取数据
    title = str(row[title_idx] or "").strip()
    question = str(row[question_idx] or "").strip()
    answer = str(row[answer_idx] or "").strip()
    difficulty = str(row[diff_idx] or "中等").strip()

    # 替换真实换行为程序换行
    question = question.replace('\n', '\\n').replace('\r', '')
    answer = answer.replace('\n', '\\n').replace('\r', '')

    # 拼接成竖线格式
    line = f"{title}|{question}|{answer}|{difficulty}"
    lines.append(line)

# 生成 TXT 文件
with open('SoupDatabase.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
