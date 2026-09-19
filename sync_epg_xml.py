import xml.etree.ElementTree as ET
import gzip
import requests

# ========== 1. 目标频道列表（来自 YD8M.txt） ==========
TARGET_CHANNELS = [
    "CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5", "CCTV6", "CCTV7", "CCTV8",
    "CCTV9", "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15",
    "CCTV5+", "CCTV17",
    "东方卫视", "东南卫视", "湖南卫视", "浙江卫视", "山东卫视", "江苏卫视",
    "黑龙江卫视", "湖北卫视", "江西卫视", "辽宁卫视", "安徽卫视", "重庆卫视",
    "天津卫视", "河南卫视", "广西卫视",
    "北京纪实科教", "金鹰纪实", "金鹰卡通", "东方财经", "法治天地",
    "海南卫视", "云南卫视", "吉林卫视", "河北卫视", "贵州卫视",
    "北京卫视4K", "湖南卫视4K", "东方卫视4K", "广东卫视4K", "深圳卫视4K",
    "江苏卫视4K", "浙江卫视4K", "山东卫视4K", "四川卫视4K", "河南卫视4K",
    "求索纪录4K", "CCTV4K", "多彩文体4K",
    "河南电视剧", "河南都市", "河南法治", "河南民生", "河南新闻", "河南公共",
    "动漫秀场", "乐游", "都市剧场",
    "CHC影迷电影", "CHC动作电影", "CHC家庭影院",
    "CCTV兵器科技", "CCTV第一剧场", "CCTV怀旧剧场", "CCTV风云音乐",
    "CCTV风云剧场", "CCTV世界地理", "CCTV卫生健康", "CCTV文化精品",
    "三门峡", "梨园频道",
]
EPG_URL = "https://github.com/mytv-android/myEPG/raw/refs/heads/master/output/epg.xml"
r = requests.get(EPG_URL, timeout=120)
r.raise_for_status()                       # 4xx/5xx 直接抛异常

mytv_epg = r.content                       # bytes
# ========== 3. 解析 EPG.xml ==========
print("正在解析 EPG.xml ...")
root = ET.fromstring(mytv_epg)          


# 建立：channel id -> 归一化后的 display-name 列表
channel_id_to_names = {}
for ch in root.findall("channel"):
    cid = ch.get("id")
    names = []
    for dn in ch.findall("display-name"):
        if dn.text:
            names.append(dn.text)
    channel_id_to_names[cid] = names

# 找出命中的 channel id
matched_ids = set()
for cid, names in channel_id_to_names.items():
    if  any(name in  TARGET_CHANNELS  for name in names) :
        matched_ids.add(cid)

print(f"EPG 中共有 channel: {len(channel_id_to_names)}")
print(f"命中目标频道数: {len(matched_ids)}")
print("命中的 id:", matched_ids)


# ========== 4. 构造新的 XML（只保留命中的 channel 和 programme） ==========
new_root = ET.Element("tv", {"date": root.get("date", "")})

# 4.1 保留命中的 channel 定义
for ch in root.findall("channel"):
    if ch.get("id") in matched_ids:
        new_root.append(ch)

# 4.2 保留命中的 programme
count = 0
for prog in root.findall("programme"):
    if prog.get("channel") in matched_ids:
        new_root.append(prog)
        count += 1

print(f"保留 programme 数: {count}")

# ========== 5. 压缩文件 ==========
new_tree = ET.ElementTree(new_root)

with gzip.open("epg_henan.xml.gz", "wb") as f:
    new_tree.write(f, encoding="utf-8", xml_declaration=True)
    print("已生成 epg_henan.xml.gz")
