#!/usr/bin/env python3
"""upload_reports_to_gd.py — 补传 reports/ 全部未上传文件到 Google Drive(V16.4.1)

复用 gd_uploader 的完整 GD 逻辑(init_gd/文件夹规则/上传), 差异点:
  已存在(网盘同名文件) → 跳过, 只上传缺失文件。

规则(与 gd_uploader 一致):
  - {code}_{type}_{ts}.txt (sht/med/lng) → 股票子文件夹「{code}-名」
  - get_val_report_*.txt / get_mak_report_*.txt → 类型文件夹 val/mak

用法:
  python scripts/upload_reports_to_gd.py [--dry-run] [--dir reports]
"""
import sys, io, os, re, argparse

for _s in (sys.stdout, sys.stderr):
    if _s is not None and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_STOCK_RE = re.compile(r"^(\d{6})_(sht|med|lng)_\d{8}_\d{4}\.txt$")
_TYPE_RE = re.compile(r"^get_(val|mak)_report_\d{8}_\d{4}\.txt$")


def _get_stock_name_map():
    """ZHB 全市场 代码→名称(本地,零网络); 缺失时用 code 兜底。"""
    try:
        from core.zhb_client import get_zhb
        zhb = get_zhb()
        if zhb is not None:
            return zhb.unified_name_map or {}
    except Exception:
        pass
    return {}


def list_all_files(drive, folder_id):
    """列出文件夹内全部文件名(分页)。"""
    names = set()
    page_token = None
    while True:
        resp = drive.files().list(
            q=f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder' and trashed=false",
            fields="nextPageToken, files(name)", pageSize=200, pageToken=page_token,
        ).execute()
        names.update(f["name"] for f in resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return names


def list_child_folders(drive, parent_id):
    """列出父文件夹下的全部子文件夹 {name: id}(分页)。"""
    folders = {}
    page_token = None
    while True:
        resp = drive.files().list(
            q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="nextPageToken, files(id, name)", pageSize=100, pageToken=page_token,
        ).execute()
        for f in resp.get("files", []):
            folders[f["name"]] = f["id"]
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return folders


def main():
    ap = argparse.ArgumentParser(description="补传 reports/ 未上传文件到 GD")
    ap.add_argument("--dry-run", action="store_true", help="只扫描并输出计划, 不实际上传")
    ap.add_argument("--dir", default=os.path.join(_ROOT, "reports"), help="报告目录")
    args = ap.parse_args()

    reports_dir = args.dir
    files = sorted(f for f in os.listdir(reports_dir) if f.endswith(".txt"))
    if not files:
        print(f"reports 目录无文件: {reports_dir}")
        return

    # 解析目标文件夹
    from core.gd_uploader import (_make_stock_folder_name, init_gd,
                             upload_report_to_drive, retry_get_folder_interactive)

    name_map = _get_stock_name_map()
    targets = {}  # folder_name -> [本地文件名...]
    for fn in files:
        m = _STOCK_RE.match(fn)
        if m:
            code, rtype = m.group(1), m.group(2)
            fname = name_map.get(code, "") or ""
            folder = _make_stock_folder_name(code, fname)
            targets.setdefault(folder, []).append(fn)
            continue
        m = _TYPE_RE.match(fn)
        if m:
            targets.setdefault(m.group(1), []).append(fn)
            continue
        print(f"  ⚠️ 无法识别文件类型, 跳过: {fn}")

    print(f"本地报告 {len(files)} 个, 目标文件夹 {len(targets)} 个:")
    for folder, fns in sorted(targets.items()):
        print(f"  「{folder}」: {len(fns)} 个")

    if args.dry_run:
        print("\n[dry-run] 完成, 未上传")
        return

    drive, proxy_set, root_id, skip_upload = init_gd(_ROOT)
    if not drive or not root_id or skip_upload:
        print("❌ GD 初始化失败或跳过上传")
        return

    # 根下已有子文件夹(避免名称漂移重复建文件夹)
    existing_folders = list_child_folders(drive, root_id)
    print(f"\n网盘根文件夹已存在 {len(existing_folders)} 个子文件夹")

    uploaded, skipped, failed = 0, 0, 0
    for folder, fns in sorted(targets.items()):
        # 定位目标文件夹: 已存在则复用; 否则按前缀匹配(如 {code}-*)或新建
        folder_id = existing_folders.get(folder)
        if folder_id is None:
            code_part = folder.split("-")[0]
            match = [fid for fname, fid in existing_folders.items()
                     if fname.startswith(code_part + "-")]
            if match:
                folder_id = match[0]
                folder = [fname for fname, fid in existing_folders.items() if fid == folder_id][0]
        if folder_id is None:
            if args.dry_run:
                continue
            folder_id = retry_get_folder_interactive(drive, folder, root_id, max_auto_retry=3)
            if folder_id:
                existing_folders[folder] = folder_id
        if not folder_id:
            print(f"  ⚠️ 文件夹获取失败, 跳过该组: {folder}")
            failed += len(fns)
            continue

        existing_files = list_all_files(drive, folder_id)
        print(f"\n🚀 「{folder}」: 网盘已有 {len(existing_files)} 个文件")
        for fn in fns:
            local_path = os.path.join(reports_dir, fn)
            if fn in existing_files:
                print(f"  ⏭️ 已存在, 跳过: {fn}")
                skipped += 1
                continue
            if args.dry_run:
                print(f"  📤 待上传: {fn}")
                continue
            try:
                if upload_report_to_drive(drive, local_path, folder_id, fn):
                    print(f"  ✅ 上传成功: {fn}")
                    uploaded += 1
                    existing_files.add(fn)
                else:
                    print(f"  ⚠️ 上传失败: {fn}")
                    failed += 1
            except Exception as e:
                print(f"  ❌ 上传异常 {fn}: {str(e)[:120]}")
                failed += 1

    print(f"\n{'='*50}")
    print(f"完成: 上传 {uploaded} | 跳过(已存在) {skipped} | 失败 {failed}")
    if proxy_set:
        try:
            from core.gd_uploader import cleanup_gd_proxy
            cleanup_gd_proxy(proxy_set)
        except Exception:
            pass


if __name__ == "__main__":
    main()
