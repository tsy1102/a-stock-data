import re, os, glob, json, collections

files = sorted(glob.glob("reports/*20260828*.md"))
# 标准章节
STD = ["一、","二、","三、","四、","五、","六、","七、","八、","九、","十、","十一、","十二、","十三、","十四、","十五、"]
CN = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10,"十一":11,"十二":12,"十三":13,"十四":14,"十五":15}

results = {}
for f in files:
    txt = open(f, encoding="utf-8", errors="replace").read()
    heads = re.findall(r"^##\s+(.+?)\s*$", txt, re.M)
    # 提取中文序号
    got = []
    titles = {}
    for h in heads:
        m = re.match(r"^([一二三四五六七八九十]+)、", h)
        if m:
            k = m.group(1)
            n = CN.get(k)
            if n:
                got.append(n)
                titles[n] = h
        else:
            titles[h] = h
    missing = [i for i in range(1,16) if i not in got]
    has_pos = any("仓位管理" in h for h in heads)
    results[os.path.basename(f)] = {"missing": missing, "n_heads": len(heads),
                                    "has_position": has_pos, "titles": {str(k):v for k,v in titles.items()},
                                    "size": os.path.getsize(f)}

json.dump(results, open(".tmp_audit/sections.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

for k,v in results.items():
    flag = "OK " if not v["missing"] and v["has_position"] else "!!!"
    miss = ",".join(str(x) for x in v["missing"]) or "-"
    print(f"{flag} {k:42s} 缺章:{miss:12s} 章节数:{v['n_heads']:2d} 仓位建议:{'Y' if v['has_position'] else 'N'} 字节:{v['size']}")
