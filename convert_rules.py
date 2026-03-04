#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import os
from datetime import datetime

# 规则源 URL 列表
SOURCES = [
    "https://easylist.to/easylist/easylist.txt",
    "https://easylist.to/easylist/easyprivacy.txt"
]

def fetch_rules(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text.splitlines()

def generate_shadowrocket_rules():
    shadowrocket_rules = []
    
    for url in SOURCES:
        lines = fetch_rules(url)
        for rule in lines:
            rule = rule.strip()
            if not rule or rule.startswith("!"):
                continue
            if rule.startswith("||"):
                # ���掉开头 "||"，去掉尾部 "^"
                domain = re.sub(r"\^$", "", rule[2:])
                shadowrocket_rules.append(f"DOMAIN-SUFFIX,{domain},REJECT")
    
    # 去重并排序
    shadowrocket_rules = sorted(set(shadowrocket_rules))
    return shadowrocket_rules

def generate_clash_rules():
    clash_rules = []
    
    for url in SOURCES:
        lines = fetch_rules(url)
        for rule in lines:
            rule = rule.strip()
            if not rule or rule.startswith("!"):
                continue
            if rule.startswith("||"):
                # 去掉开头 "||"，去掉尾部 "^"
                domain = re.sub(r"\^$", "", rule[2:])
                clash_rules.append(f"  - '+.{domain}'")
    
    # 去重并排序
    clash_rules = sorted(set(clash_rules))
    return clash_rules

def main():
    # 创建输出目录
    os.makedirs("docs", exist_ok=True)
    
    # 生成 Shadowrocket 规则
    shadowrocket_rules = generate_shadowrocket_rules()
    sr_path = os.path.join("docs", "REJECT.txt")
    with open(sr_path, "w", encoding="utf-8") as f:
        f.write("\n".join(shadowrocket_rules))
    print(f"Generated {sr_path}: {len(shadowrocket_rules)} rules")
    
    # 生成 Clash 规则
    clash_rules = generate_clash_rules()
    clash_path = os.path.join("docs", "REJECT.yaml")
    with open(clash_path, "w", encoding="utf-8") as f:
        # 写入头部注释
        f.write("# Clash YAML 格式规则集\n")
        f.write("# 生成时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("# 来源：https://easylist.to/easylist/easylist.txt\n")
        f.write("# 来源：https://easylist.to/easylist/easyprivacy.txt\n")
        f.write("payload:\n")
        f.write("\n".join(clash_rules))
    print(f"Generated {clash_path}: {len(clash_rules)} rules")

if __name__ == "__main__":
    main()