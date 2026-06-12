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

# ... (前面的获取 Token 和 Table ID 代码保持不变) ...

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

    title = get_text("标题", "无题").strip()
    question = get_text("谜面", "").strip()
    answer = get_text("谜底", "").strip()
    difficulty = get_text("难度", "中等").strip()

    if not question:
        continue

    # 处理多余换行符
    question = question.replace('\n', '\\n').replace('\r', '')
    answer = answer.replace('\n', '\\n').replace('\r', '')

    line_str = f"{title}|{question}|{answer}|{difficulty}"

    # 🌟 核心分拣逻辑：认出“规则”并单独存放
    if "规则" in title or "指南" in title:
        rule_line = line_str
    else:
        normal_lines.append(line_str)

# 🌟 本地极速排序：把普通汤直接倒置，最新的瞬间排到最前面！
normal_lines.reverse()

# 🌟 强行置顶：把规则无条件塞到第一位
final_lines = []
if rule_line:
    final_lines.append(rule_line)
final_lines.extend(normal_lines)

print(f"成功抓取并排序 {len(final_lines)} 条海龟汤！")
with open('SoupDatabase.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(final_lines))
