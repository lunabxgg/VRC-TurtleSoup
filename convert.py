import os
import requests
import json

# 从 GitHub 保险柜里拿出刚才存的钥匙
APP_ID = os.environ.get("FEISHU_APP_ID")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET")
APP_TOKEN = os.environ.get("FEISHU_APP_TOKEN")

print("正在获取飞书通行证...")
auth_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
auth_res = requests.post(auth_url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
access_token = auth_res.get("tenant_access_token")

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

print("正在寻找海龟汤数据表...")
tables_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables"
tables_res = requests.get(tables_url, headers=headers).json()
table_id = tables_res['data']['items'][0]['table_id']

print("正在从飞书直抽原始数据(极速模式)...")
# 🌟 删掉了拖慢速度的 view_id 参数，恢复极速拿取
records_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records?page_size=500"
records_res = requests.get(records_url, headers=headers).json()
items = records_res.get('data', {}).get('items', [])

normal_lines = []
rule_line = ""

for item in items:
    fields = item.get('fields', {})
    
    # 依然只抓取过审的数据
    is_approved = fields.get("过审", False)
    if not is_approved:
        continue

    def get_text(key_word, default=""):
        actual_key = next((k for k in fields.keys() if key_word in k), None)
        if not actual_key: return default
        field_data = fields.get(actual_key)
        if not field_data: return default
        if isinstance(field_data, list):
            return "".join([str(x.get('text', '')) for x in field_data])
        return str(field_data)

    # 🌟 新增：格式检查与内容清洗函数
    def clean_format(text):
        if not text: 
            return ""
        # 1. 删掉文本段落中可能出现的分割符 |，避免 txt 格式混乱
        text = text.replace('|', '')
        # 2. 精准识别指定的特殊标签整体，统一替换为 [/]
        target_tags = ['[/r]', '[/o]', '[/y]', '[/g]', '[/c]', '[/b]', '[/p]']
        for tag in target_tags:
            text = text.replace(tag, '[/]')
            text = text.replace(tag.upper(), '[/]')  # 顺便兼容大写，如 [/R] 也会被替换
        return text

    # 获取数据并同时进行格式检查清洗
    title = clean_format(get_text("标题", "无题").strip())
    question = clean_format(get_text("谜面", "").strip())
    answer = clean_format(get_text("谜底", "").strip())
    difficulty = clean_format(get_text("难度", "中等").strip())
    
    # 🌟 提取“序”或“序号”字段的值（由于是用于判断的数字/序号，保持原样即可）
    xu_number = get_text("序", "").strip()

    if not question:
        continue

    # 处理多余换行符
    question = question.replace('\n', '\\n').replace('\r', '')
    answer = answer.replace('\n', '\\n').replace('\r', '')

    line_str = f"{title}|{question}|{answer}|{difficulty}"

    # 🌟 核心分拣逻辑：精准认出“序”为 5 的记录并单独存放
    # 飞书 API 传回来的数字有时是 "5"，有时会带小数点变成 "5.0"，所以做个兼容
    if xu_number == "5" or xu_number == "5.0":
        rule_line = line_str
    else:
        normal_lines.append(line_str)

# 🌟 本地极速排序：把普通汤直接倒置，最新的瞬间排到最前面！
normal_lines.reverse()

# 🌟 强行置顶：把抽出来的 5 号无条件塞到第一位
final_lines = []
if rule_line:
    final_lines.append(rule_line)
else:
    print("⚠️ 警告：没有找到'序'为 5 的记录，请检查飞书表格！")
    
final_lines.extend(normal_lines)

print(f"成功抓取并排序 {len(final_lines)} 条海龟汤！")
with open('SoupDatabase.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(final_lines))

# 🌟 新增：主动请求 jsDelivr 清理缓存
print("正在呼叫 jsDelivr 清理 CDN 缓存...")
try:
    purge_url = "https://purge.jsdelivr.net/gh/lunabxgg/VRC-TurtleSoup@main/SoupDatabase.txt"
    purge_res = requests.get(purge_url, timeout=10)
    print(f"缓存清理完成！状态码: {purge_res.status_code}")
except Exception as e:
    print(f"缓存清理请求失败: {e}")
