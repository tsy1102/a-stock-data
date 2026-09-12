"""真机验证：用修复后的 _parse_tdxstat 解析真实 zhb.zip，确认 8 个遗漏列已抽取。"""
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.zhb_client import ZhbData

ZHBDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "zhb")
DATE = "20260911"  # 该日期 zip 必存在（周六采集=周五收盘）


def find_tdxstat(zf):
    for n in zf.namelist():
        if n.endswith("tdxstat.cfg"):
            return n
    return None


def main():
    fp = os.path.join(ZHBDIR, f"zhb_{DATE}.zip")
    if not os.path.exists(fp):
        print(f"MISSING {fp}")
        return 1
    with zipfile.ZipFile(fp) as zf:
        name = find_tdxstat(zf)
        data = zf.read(name)
    d = ZhbData()
    d.date = DATE
    d.raw_files = {"tdxstat.cfg": data}
    res = d._parse_tdxstat()
    print(f"[OK] 解析 {len(res)} 只股票")

    new_cols = ["unknown_2", "free_ltgb", "rd_input_fee", "shape_value",
                "zt_type_code", "pre_receive_zj", "unknown_26", "other_qy_jzc"]
    # 检查新列非空覆盖率
    cov = {c: 0 for c in new_cols}
    sample = {}
    for code, row in res.items():
        for c in new_cols:
            v = row.get(c)
            if v not in (None, "", ):
                cov[c] += 1
        if len(sample) < 5:
            sample[code] = {c: row.get(c) for c in new_cols}
    print("\n[覆盖率] 新列非空股数 / 总股数:")
    for c in new_cols:
        print(f"  {c:14s} {cov[c]:5d} / {len(res)}")
    print("\n[样本] 前 5 只:")
    for code, row in sample.items():
        sv = row["shape_value"]
        print(f"  {code}: shape_value={sv!r} free_ltgb={row['free_ltgb']} zt_type_code={row['zt_type_code']} unknown_26={row['unknown_26']} other_qy_jzc={row['other_qy_jzc']}")
    # 断言：shape_value 应有较高非空率（动态码，少数可能为空）
    ok = cov["shape_value"] > len(res) * 0.5
    print(f"\n[断言] shape_value 非空率={cov['shape_value']/len(res):.1%} -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
