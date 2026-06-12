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

print("正在从飞书直抽数据...")
# 获取最多 500 条数据 (题量超过500后可在此处加翻页逻辑)
# 🌟 强行指定视图 ID，机器人就会乖乖按照你排好的顺序抓取了！
records_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records?page_size=500&view_id=vewqWDFxin"
records_res = requests.get(records_url, headers=headers).json()
items = records_res.get('data', {}).get('items', [])

lines = []
for item in items:
    fields = item.get('fields', {})
    
    # 🌟 终极筛选：只抓取你在飞书里打勾了 "过审" 的数据！
    is_approved = fields.get("过审", False)
    if not is_approved:
        continue

    def get_text(key_word, default=""):
        # 智能模糊匹配你截图里的列名，哪怕你以后改名了也能认出来
        actual_key = next((k for k in fields.keys() if key_word in k), None)
        if not actual_key: return default
        
        field_data = fields.get(actual_key)
        if not field_data: return default
        if isinstance(field_data, list):
            # 兼容飞书的多段富文本
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

    lines.append(f"{title}|{question}|{answer}|{difficulty}")

print(f"成功抓取 {len(lines)} 条已过审的海龟汤！正在生成 TXT...")
with open('SoupDatabase.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
