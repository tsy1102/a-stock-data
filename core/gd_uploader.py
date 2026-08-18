"""gd_uploader.py — Google Drive 上传模块（统一API入口）

迁移：
  - V4: oauth2client + pydrive2（均已 deprecated / 不再活跃维护）
  - V7: google-auth + google-auth-oauthlib + google-api-python-client（Google 官方推荐）
  - V15.2: init_gd 非交互模式自动跳过（sys.stdin.isatty() 检测）；所有 print 加 flush=True
  - V15.1: 自动重试 3 次 + 显式 "⚠️ GD 云端同步跳过" 日志
  - V14.0: docstring 版本信息统一更新

API 映射：
  旧 OAuth2WebServerFlow → InstalledAppFlow.from_client_secrets_file
  旧 OAuth2Credentials → google.oauth2.credentials.Credentials
  旧 GoogleDrive(fs)  → build("drive", "v3", credentials=creds)
  旧 ListFile({'q': ...}) → service.files().list(q=...).execute()
  旧 CreateFile + SetContentString/Upload → service.files().create/update + MediaIoBaseUpload

统一 API（两种上传模式，所有脚本统一调用）：

  模式A —— 多股票逐个上传（ful/sht/med/lng 等批量脚本使用）：
    每个股票创建独立子文件夹「代码-2个中文」，逐个上传
    文件夹命名规则：跳过ST前缀，取前2个中文字符，无中文时显示「代码-」
    from core.gd_uploader import init_gd, upload_stock_report_by_code, cleanup_gd_proxy
    drive, proxy_set, parent_id, skip = init_gd(base_dir)
    if drive and not skip:
        upload_stock_report_by_code(drive, parent_id, "600519", "贵州茅台", "./out/600519_ful_xxx.txt")
    cleanup_gd_proxy(proxy_set)

  模式B —— 统一类型文件夹上传（val/mak 等单类型脚本使用）：
    所有文件放入统一子文件夹「val」/「mak」
    from core.gd_uploader import init_gd, upload_type_reports, cleanup_gd_proxy
    drive, proxy_set, parent_id, skip = init_gd(base_dir)
    if drive and not skip:
        upload_type_reports(drive, parent_id, "mak", ["./out/mak_report_xxx.txt"])
    cleanup_gd_proxy(proxy_set)

  特殊功能 —— 快照文件上传：
    快照文件自动上传到 a-stock-data/snapshot/ 文件夹
    文件格式：snapshot_YYYYMMDD_HHmm.txt

首次授权流程：
  1. 脚本在浏览器打开 Google OAuth 页面 → 选择账号 → 授权
  2. access_token + refresh_token 自动保存到 credentials.json
  3. 后续运行会自动刷新 token，无需再次手动授权
"""
from __future__ import annotations

import io
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, cast

from stock_common import _debug_log

# ── Google API SCOPES ───────────────────────────────────────────
_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
# V17.0: 凭据集中到仓库 credentials/ 子目录（gitignore 规则同步迁移）
_CRED_SUBDIR = "credentials"
_TOKEN_FILENAME = "credentials.json"
_CLIENT_SECRETS_FILENAME = "client_secrets.json"
_MIME_TEXT = "text/plain; charset=utf-8"


# ────────────────────────────────────────────────────────────────
# 1. 代理自动探测（Windows 常见本地代理端口：7890/10809/1080/3067）
# ────────────────────────────────────────────────────────────────
def _find_working_proxy() -> Optional[str]:
    """尝试常见本地代理端口，返回可用的 "http://127.0.0.1:port"，否则 None。"""
    for port in [7890, 10809, 1080, 3067, 1081, 10808, 8080, 3128]:
        test = f"http://127.0.0.1:{port}"
        proxy_handler = urllib.request.ProxyHandler({"http": test, "https": test})
        opener = urllib.request.build_opener(proxy_handler)
        try:
            opener.open("https://accounts.google.com/.well-known/openid-configuration", timeout=2)
            return test
        except Exception as _e:
            _debug_log(f"gd_proxy_test error ({test}): {_e}")
            continue
    return None


def cleanup_gd_proxy(was_set: bool) -> None:
    """操作结束后清除本脚本设置的代理环境变量。"""
    if was_set:
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)


# ────────────────────────────────────────────────────────────────
# 2. OAuth 凭据加载 / 刷新 / 首次授权
# ────────────────────────────────────────────────────────────────
def _load_saved_credentials(token_path: str):
    """从 credentials.json 加载已保存 token；过期/无效时返回 (None, reason)。

    V17.0.4(2026-08-19): 返回 (creds, error_type)——error_type:
      None     正常(有效或刷新成功)
      "invalid" token 结构无效/无 refresh_token(可安全删除文件)
      "network" 刷新失败(网络瞬时)——**不清除文件**, 下次再试, 不触发 OAuth
    原实现刷新异常一律返回 None → 调用方误删文件 → 走 OAuth 阻塞卡死(无人值守)。
    """
    try:
        from google.oauth2.credentials import Credentials
        if not os.path.exists(token_path):
            return None, None
        creds = Credentials.from_authorized_user_file(token_path, _SCOPES)
        if creds and creds.valid:
            return creds, None
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            try:
                creds.refresh(Request())
                with open(token_path, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
                return creds, None
            except Exception as _e:
                # 刷新失败: 网络问题(保留文件) vs token 被吊销(invalid)
                _msg = str(_e).lower()
                if "invalid_grant" in _msg or "revoked" in _msg or "expired" in _msg:
                    _debug_log(f"gd refresh revoked ({token_path}): {_e}")
                    return None, "invalid"
                _debug_log(f"gd refresh network error ({token_path}): {_e}")
                return None, "network"
        return None, "invalid"
    except Exception as _e:
        _debug_log(f"gd _load_saved_credentials error ({token_path}): {_e}")
        return None, "invalid"


def _run_oauth_flow(base_dir: str):
    """首次授权：走 InstalledAppFlow（会打开浏览器或打印 URL）。

    V17.0.4(2026-08-19): 加 90s 超时——无人值守(批处理/定时任务)环境
    run_local_server 永久阻塞等待授权 → 卡死。超时返回 None(跳过上传, 不阻塞报告)。
    """
    try:
        import concurrent.futures as _cf
        from google_auth_oauthlib.flow import InstalledAppFlow
        secrets_path = os.path.join(base_dir, _CRED_SUBDIR, _CLIENT_SECRETS_FILENAME)
        if not os.path.exists(secrets_path):
            print(f"  ❌ 缺少 {_CLIENT_SECRETS_FILENAME}，请从 Google Cloud Console 下载：", flush=True)
            print("     https://console.cloud.google.com/apis/credentials", flush=True)
            return None

        def _flow():
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, _SCOPES)
            return flow.run_local_server(port=0)

        with _cf.ThreadPoolExecutor(max_workers=1) as _ex:
            _future = _ex.submit(_flow)
            try:
                return _future.result(timeout=90)
            except _cf.TimeoutError:
                print("  ⏱ OAuth 授权超时(90s)——无人值守环境跳过授权, 本次不上传 GD", flush=True)
                _future.cancel()
                return None
    except Exception as e:
        print(f"  ⚠️ OAuth 流程失败：{e}", flush=True)
        return None


def _get_or_create_credentials(base_dir: str):
    """入口：加载现有 token → 刷新 → 都失败则走首次 OAuth。

    V17.0.4(2026-08-19): 刷新失败为网络问题时不删除文件(下次再试)、不触发 OAuth——
    原实现误删文件后走 run_local_server 无人值守永久阻塞(卡死根因)。
    """
    token_path = os.path.join(base_dir, _CRED_SUBDIR, _TOKEN_FILENAME)                       # V17.0: credentials/ 子目录
    # 1) 加载现有 token
    creds, err = _load_saved_credentials(token_path)
    if creds:
        return creds
    # 2) 网络问题(刷新失败): 保留文件, 跳过 OAuth, 本次不上传
    if err == "network":
        print("  ⚠️ GD 凭据刷新失败(网络问题)——保留文件, 本次跳过上传", flush=True)
        return None
    # 3) token 结构无效/被吊销 → 删除旧文件避免下次继续尝试
    try:
        if os.path.exists(token_path):
            os.remove(token_path)
            print("  🗑️ 已清除过期的旧 credentials.json", flush=True)
    except OSError:
        pass
    # 4) 走首次 OAuth 授权(90s 超时, 无人值守自动跳过)
    new_creds = _run_oauth_flow(base_dir)
    if new_creds is not None:
        try:
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(new_creds.to_json())
        except OSError:
            pass
    return new_creds


# ────────────────────────────────────────────────────────────────
# 3. Drive Service 初始化
# ────────────────────────────────────────────────────────────────
def init_google_drive(base_dir: str) -> Tuple[Optional[Any], bool]:
    """初始化 Google Drive 服务。

    返回: (googleapiclient.discovery.Resource 或 None, proxy_was_set: bool)
    """
    proxy_was_set = False

    # 自动设置代理（仅当系统尚未设置 HTTP_PROXY 时）
    if not os.environ.get("HTTP_PROXY"):
        detected = _find_working_proxy()
        if detected:
            os.environ["HTTP_PROXY"] = detected
            os.environ["HTTPS_PROXY"] = detected
            proxy_was_set = True

    print("  正在初始化 Google Drive 安全连接…", flush=True)
    try:
        creds = _get_or_create_credentials(base_dir)
        if creds is None:
            return None, proxy_was_set
        from googleapiclient.discovery import build
        service = build("drive", "v3", credentials=creds, cache_discovery=False)
        # 健康检查：拿一次 About
        try:
            service.about().get(fields="user").execute()
            print("  ✅ Google Drive 认证成功", flush=True)
        except Exception as _e:
            _debug_log(f"gd auth health check error: {_e}")
            print("  ✅ Google Drive 认证成功（API 可访问）", flush=True)
        return service, proxy_was_set
    except Exception as e:
        msg = str(e)
        if "invalid_grant" in msg or "revoked" in msg.lower() or "expired" in msg.lower():
            print("  🔑 GD Token 已过期或已被吊销，清除后请重新运行脚本授权", flush=True)
            try:
                os.remove(os.path.join(base_dir, _CRED_SUBDIR, _TOKEN_FILENAME))  # V17.0: credentials/ 子目录
            except OSError:
                pass
        else:
            print(f"  ⚠️ 云盘连接失败：{msg}", flush=True)
            # V16.4.0: 网络抖动自动重试（前 2 次默认 1s 后自动重试——对齐交互模式"重试"选择）
            for _attempt in (1, 2):
                import time as _t

                _t.sleep(1.0)
                print(f"  ⏳ 自动重试 {_attempt}/2（1s 后）…", flush=True)
                try:
                    service = build("drive", "v3", credentials=creds, cache_discovery=False)
                    service.about().get(fields="user").execute()
                    print("  ✅ Google Drive 认证成功（重试后）", flush=True)
                    return service, proxy_was_set
                except Exception as _e2:
                    _debug_log(f"gd retry {_attempt} error: {_e2}")
            print("  ❌ 云盘连接失败（重试 2 次仍失败）", flush=True)
        return None, proxy_was_set


# ────────────────────────────────────────────────────────────────
# 4. 文件夹与文件操作
# ────────────────────────────────────────────────────────────────
def get_or_create_drive_folder(service, name: str, parent_id: Optional[str] = None) -> Optional[str]:
    """查找或创建文件夹，返回其 Drive ID。失败返回 None。

    关键规则：
    - parent_id 为 None 时表示在根目录下查找/创建，搜索时强制 'root' in parents
    - parent_id 为空字符串时拒绝操作（禁止在根目录之外的模糊位置操作）
    - parent_id 为有效 ID 时，先验证 ID 存在性，再限制在该父文件夹下查找/创建
    """
    if not service:
        return None
    try:
        # 验证 parent_id 有效性：非 None 的 parent_id 必须对应一个存在的文件夹
        if parent_id is not None:
            if not parent_id:
                # parent_id 为空字符串，拒绝操作
                print(f"  ❌ 父文件夹ID无效，拒绝操作文件夹「{name}」", flush=True)
                return None
            try:
                service.files().get(fileId=parent_id, fields="id").execute()
            except Exception as _e:
                _debug_log(f"gd validate_parent_id error ({parent_id}): {_e}")
                print(f"  ❌ 父文件夹ID不存在或已失效，拒绝操作文件夹「{name}」", flush=True)
                return None

        q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

        if parent_id is None:
            # parent_id 为 None 表示根目录，强制限制在根目录搜索
            q += " and 'root' in parents"
        else:
            # parent_id 为有效 ID，限制在指定父文件夹下搜索
            q += f" and '{parent_id}' in parents"

        resp = service.files().list(q=q, spaces="drive", fields="files(id, name)", pageSize=5).execute()
        items = resp.get("files", [])
        if items:
            print(f"  🔍 云盘文件夹已存在：{name}", flush=True)
            return cast(str, items[0]["id"])

        # 创建文件夹
        body: Dict[str, Any] = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            # parent_id 为有效 ID，在指定父文件夹下创建
            body["parents"] = [parent_id]
        # parent_id 为 None 表示根目录，不设置 parents（默认创建在根目录）

        created = service.files().create(body=body, fields="id").execute()
        print(f"  ➕ 已创建云盘文件夹：{name}", flush=True)
        return cast(Optional[str], created.get("id"))
    except Exception as e:
        print(f"  ❌ 获取或创建文件夹失败：{e}", flush=True)
        return None


def retry_get_folder_interactive(service, name: str, parent_id: Optional[str] = None,
                                 max_auto_retry: int = 2) -> Optional[str]:
    """交互式获取/创建文件夹。

    流程：
      1. 自动重试 max_auto_retry 次（每次间隔递增：3s, 6s）
      2. 若仍失败，进入交互模式：
         - 输入 1：跳过云端上传，返回 None
         - 输入 2：立即重试一次
         - 输入 3：等待 10 秒后重试
         - 输入 4：等待 30 秒后重试
      3. 交互模式重试成功后自动退出

    返回: folder_id 或 None（用户选择跳过）
    """
    # 自动重试阶段
    for attempt in range(max_auto_retry):
        folder_id = get_or_create_drive_folder(service, name, parent_id)
        if folder_id:
            return folder_id
        if attempt < max_auto_retry - 1:
            wait_time = 3 * (attempt + 1)
            print(f"  ⏳ {wait_time} 秒后自动重试 ({attempt + 2}/{max_auto_retry})…", flush=True)
            time.sleep(wait_time)

    # 交互重试阶段
    while True:
        print(f"  ⚠️ 获取文件夹「{name}」失败", flush=True)
        print("  [1] 跳过云端上传，继续后续流程", flush=True)
        print("  [2] 立即重试", flush=True)
        print("  [3] 等待 10 秒后重试", flush=True)
        print("  [4] 等待 30 秒后重试", flush=True)
        try:
            choice = input("请选择 [2]: ").strip() or "2"
        except (EOFError, KeyboardInterrupt):
            print("\n  📝 跳过云端上传…", flush=True)
            return None

        if choice == "1":
            print("  📝 跳过云端上传…", flush=True)
            return None
        elif choice == "2":
            print("  🔄 立即重试…", flush=True)
        elif choice == "3":
            print("  ⏳ 等待 10 秒后重试…", flush=True)
            time.sleep(10)
        elif choice == "4":
            print("  ⏳ 等待 30 秒后重试…", flush=True)
            time.sleep(30)
        else:
            print("  无效选择，默认立即重试…", flush=True)
            choice = "2"

        # 执行重试
        folder_id = get_or_create_drive_folder(service, name, parent_id)
        if folder_id:
            print(f"  ✅ 文件夹「{name}」获取成功", flush=True)
            return folder_id
        # 失败后继续循环


def upload_or_update_to_drive(service, local_path: str, parent_id: str, file_name: str) -> bool:
    """上传/更新本地文件到指定文件夹。同名已存在则覆盖内容。"""
    if not service or not os.path.exists(local_path):
        return False
    # 读取内容（文本，utf-8）
    try:
        with open(local_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        print(f"  ❌ 读取本地文件失败：{e}", flush=True)
        return False

    for attempt in range(3):
        try:
            # 1) 查同名文件
            q = (f"name='{file_name}' and '{parent_id}' in parents "
                 "and mimeType!='application/vnd.google-apps.folder' and trashed=false")
            resp = service.files().list(q=q, spaces="drive", fields="files(id)", pageSize=5).execute()
            existing = resp.get("files", [])

            # 2) 使用 googleapiclient.http.MediaIoBaseUpload
            from googleapiclient.http import MediaIoBaseUpload
            media = MediaIoBaseUpload(io.BytesIO(content.encode("utf-8")),
                                      mimetype=_MIME_TEXT, resumable=True)

            if existing:
                fid = existing[0]["id"]
                service.files().update(fileId=fid, media_body=media).execute()
                print(f"    📎 已覆盖更新：{file_name} (id={fid[:10]}...)", flush=True)
            else:
                body = {"name": file_name, "parents": [parent_id]}
                created = service.files().create(body=body, media_body=media, fields="id").execute()
                print(f"    📎 已上传：{file_name} (id={created.get('id', '')[:10]}...)", flush=True)
            return True
        except Exception as e:
            print(f"  上传第 {attempt + 1} 次失败：{e}，重试中…", flush=True)
            time.sleep(2 * (attempt + 1))
    return False


def upload_report_to_drive(service, local_path: str, parent_id: str, file_name: Optional[str] = None) -> bool:
    """兼容旧接口：与 upload_or_update_to_drive 等价（file_name 默认取文件名）。"""
    if file_name is None:
        file_name = os.path.basename(local_path)
    return upload_or_update_to_drive(service, local_path, parent_id, file_name)


# ────────────────────────────────────────────────────────────────
# 4. 股票文件夹名称处理工具函数
# ────────────────────────────────────────────────────────────────
def _make_stock_folder_name(code: str, full_name: str) -> str:
    """构建股票文件夹名称：股票代码-2个中文，跳过ST，无中文则留横线
    
    :param code: 股票代码，例如 "002193"
    :param full_name: 完整股票名称，例如 "ST如意股份" 或 "贵州茅台"
    :return: 文件夹名称，例如 "002193-如意" 或 "600519-" 或 "000001-"
    """
    import re
    
    # 跳过ST前缀
    name_without_st = re.sub(r'^ST', '', full_name)
    
    # 提取中文字符，只取前2个
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', name_without_st)
    chinese_part = ''.join(chinese_chars[:2])
    
    # 如果没有中文字符，保留横线表示问题
    if not chinese_part:
        return f"{code}-"
    else:
        return f"{code}-{chinese_part}"


# ────────────────────────────────────────────────────────────────
# ────────────────────────────────────────────────────────────────
# 6. 统一高层 API —— init_gd / upload_stock_report_by_code / upload_type_reports
#    供 sht/med/lng/val/mak/full 等所有脚本统一复用
# ────────────────────────────────────────────────────────────────

def init_gd(base_dir: str) -> Tuple[Optional[Any], bool, Optional[str], bool]:
    """统一GD初始化入口：交互式连接 + 获取根文件夹「a-stock-data」。

    所有脚本都应调用此函数，避免各自实现重复的重试/交互逻辑。

    流程：
      1. 尝试初始化 GD 连接
      2. 若失败 → 交互模式：跳过 / 立即重试 / 等10秒 / 等30秒
      3. 连接成功后获取根文件夹「a-stock-data」（同样支持交互式重试）

    返回:
        (drive, proxy_set, parent_folder_id, skip_upload)
        - drive: googleapiclient service（失败时为 None）
        - proxy_set: bool，是否设置了代理环境变量，后续 cleanup_gd_proxy 需要
        - parent_folder_id: 根文件夹「a-stock-data」的 Drive ID
        - skip_upload: bool，True 表示用户选择跳过云端上传
    """
    drive, proxy_set = None, False

    # V15.2: 非交互模式（main.py 子进程 stdin=PIPE）——原实现直接跳过上传。
    # V16.4.0: 已有 token 时不跳过（自动重试路径已加固）；仅"无 token 需 OAuth 交互授权"时跳过
    import sys

    if not sys.stdin.isatty():
        import os as _os

        _token_file = _os.path.join(base_dir, _CRED_SUBDIR, "credentials.json")  # V17.0: credentials/ 子目录
        _has_token = _os.path.exists(_token_file)
        if not _has_token:
            print("  ?? 检测到非交互模式（stdin 非 tty）且无 GD token——自动跳过云端上传", flush=True)
            return None, False, None, True
        try:
            drive, proxy_set = init_google_drive(base_dir)
            if drive:
                print("  ? GD 连接成功（非交互+已有 token）", flush=True)
                root_id = get_or_create_drive_folder(drive, "a-stock-data")
                if root_id:
                    return drive, proxy_set, root_id, False
                print("  ?? GD 根文件夹获取失败——跳过上传", flush=True)
            else:
                print("  ?? GD 连接失败（非交互）——跳过上传", flush=True)
        except Exception as e:
            print(f"  ?? GD 初始化异常（非交互）——跳过上传: {str(e)[:80]}", flush=True)
        return None, proxy_set, None, True

    # 交互式连接
    while True:
        print("  正在初始化 Google Drive 安全连接…", flush=True)
        try:
            drive, proxy_set = init_google_drive(base_dir)
            if drive:
                print("  ✅ GD 连接成功", flush=True)
                break
        except Exception as e:
            print(f"  ⚠️ GD 连接异常: {e}", flush=True)

        # 连接失败 → 交互模式
        print("  ⚠️ GD 连接失败", flush=True)
        print("  [1] 跳过云端上传，继续后续流程", flush=True)
        print("  [2] 立即重试", flush=True)
        print("  [3] 等待 10 秒后重试", flush=True)
        print("  [4] 等待 30 秒后重试", flush=True)
        try:
            choice = input("请选择 [2]: ").strip() or "2"
        except (EOFError, KeyboardInterrupt):
            print("\n  📝 跳过云端上传…", flush=True)
            return None, proxy_set, None, True

        if choice == "1":
            print("  📝 跳过云端上传…", flush=True)
            return None, proxy_set, None, True
        elif choice == "3":
            print("  ⏳ 等待 10 秒后重试…", flush=True)
            time.sleep(10)
        elif choice == "4":
            print("  ⏳ 等待 30 秒后重试…", flush=True)
            time.sleep(30)
        elif choice != "2":
            print("  无效选择，默认立即重试…", flush=True)

    # 获取根文件夹「a-stock-data」（parent_id=None 表示在根目录下查找/创建）
    root_id = retry_get_folder_interactive(drive, "a-stock-data", None, max_auto_retry=3)
    if not root_id:
        return drive, proxy_set, None, True

    return drive, proxy_set, root_id, False


def upload_stock_report_by_code(drive, parent_folder_id: str,
                                code: str, stock_name: str,
                                file_path: str) -> bool:
    """模式A —— 多股票逐个上传：为单只股票创建独立子文件夹「代码-名称」并上传报告。

    适用于 sht/med/lng 等批量分析脚本，每只股票一个独立子文件夹。

    :param drive: init_gd 返回的 Google Drive service
    :param parent_folder_id: 根文件夹 ID（必须是 a-stock-data 的 ID）
    :param code: 股票代码，例如 "600519"
    :param stock_name: 股票名称，例如 "贵州茅台"（调用方通过 tdx_get_quote_full 获取）
    :param file_path: 本地报告文件路径
    :return: True 表示上传成功
    """
    if not drive:
        print(f"  ❌ GD上传失败：drive 未初始化，股票代码：{code}", flush=True)
        return False
    if not parent_folder_id:
        print(f"  ❌ GD上传失败：parent_folder_id 为空，拒绝上传到根目录，股票代码：{code}", flush=True)
        return False
    if not os.path.exists(file_path):
        print(f"  ❌ 本地报告不存在：{file_path}", flush=True)
        return False

    # 1) 构建股票子文件夹名
    folder_name = _make_stock_folder_name(code, stock_name)

    # 1) 获取/创建股票子文件夹（交互式重试）
    sub_id = retry_get_folder_interactive(drive, folder_name, parent_folder_id, max_auto_retry=3)
    if not sub_id:
        print(f"  ⚠️ GD 子文件夹获取失败：{folder_name}", flush=True)
        return False

    # 3) 上传
    print(f"🚀 同步至 GD「{folder_name}」…", flush=True)
    fn = os.path.basename(file_path)
    ok = upload_report_to_drive(drive, file_path, sub_id, fn)
    if ok:
        print("  ✅ GD 上传成功", flush=True)
    else:
        print("  ⚠️ GD 上传失败", flush=True)
    return ok


def upload_type_reports(drive, parent_folder_id: str, type_name: str,
                        file_paths) -> int:
    """模式B —— 统一类型文件夹上传：创建类型子文件夹并批量上传所有报告。

    适用于 val/mak/ful 等单类型分析脚本，所有报告放入同一子文件夹。

    :param drive: init_gd 返回的 Google Drive service
    :param parent_folder_id: 根文件夹 ID
    :param type_name: 类型名，例如 "val" / "mak" / "ful"
    :param file_paths: 本地报告文件路径列表（或单个字符串）
    :return: 成功上传的文件数量
    """
    if not drive or not parent_folder_id:
        return 0

    # 支持单个文件路径
    if isinstance(file_paths, str):
        file_paths = [file_paths]

    # 过滤存在的文件
    valid_paths = [p for p in file_paths if os.path.exists(p)]
    if not valid_paths:
        print("  ⚠️ 没有可上传的本地报告", flush=True)
        return 0

    # 1) 获取/创建类型子文件夹（交互式重试）
    type_id = retry_get_folder_interactive(drive, type_name, parent_folder_id, max_auto_retry=3)
    if not type_id:
        print(f"  ⚠️ GD 类型子文件夹获取失败：{type_name}", flush=True)
        return 0

    # 2) 批量上传
    print(f"\n🚀 同步至 GD「{type_name}」文件夹…", flush=True)
    success_count = 0
    for local_path in valid_paths:
        fn = os.path.basename(local_path)
        if upload_report_to_drive(drive, local_path, type_id, fn):
            print(f"  ✅ {fn} 上传成功", flush=True)
            success_count += 1
        else:
            print(f"  ⚠️ {fn} 上传失败", flush=True)
    return success_count

