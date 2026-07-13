# 贡献指南

感谢你考虑为本项目做出贡献！

## 行为准则

请阅读 [CODE_OF_CONDUCT.md](file:///d:/GitHub/test/CODE_OF_CONDUCT.md) 了解社区行为规范。

## 提交流程

1. Fork 本仓库
2. 从 `main` 拉取特性分支（`git checkout -b feat/your-feature`）
3. 提交改动（`git commit -m "feat: your feature"`）
4. 推送分支（`git push origin feat/your-feature`）
5. 在 GitHub 上发起 Pull Request

## 代码规范

- **代码风格**：遵循 [PEP 8](https://peps.python.org/pep-0008/)，提交前请运行 `black .` 格式化
- **类型注解**：核心模块（`stock_common/`、`gd_uploader.py`、`tdx_client.py`）必须保留 PEP 484 类型注解
- **类型检查**：新增/修改核心模块前，请运行 `python -m mypy <module> --ignore-missing-imports` 自检
- **导入顺序**：标准库 → 第三方库 → 本项目（用 `isort` 自动整理）
- **日志输出**：避免 `print` 调试，统一使用 `stock_common.sc_network._debug_log` 记录异常与可观测信息
- **静默异常**：禁止 `except Exception: pass`，必须显式处理或记录日志

## 单元测试

- 新功能/修复必须在 `tests/` 目录下提供对应测试用例
- 使用 `pytest` 框架：测试函数以 `test_` 开头
- 运行方式：`pytest tests/`
- 至少保证 `tests/test_cache.py`、`tests/test_gd_uploader.py`、`tests/test_scoring.py` 通过

## 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

常用 type：
- `feat`：新增功能
- `fix`：Bug 修复
- `refactor`：重构（既不是新增功能，也不是修复 bug）
- `docs`：仅文档变更
- `test`：仅测试变更
- `chore`：构建/工具链变更

示例：
```
feat(sht): 支持 --depth medium 档分析
fix(gd): 修复 init_gd 在网络中断时挂起的问题
docs(readme): 更新依赖表格，拆分 dev 依赖
```

## 分支策略

- `main`：稳定分支，所有发布版本均打 tag 在此分支
- 主题分支：从 `main` 拉取，命名格式 `<type>/<short-desc>`（如 `fix/gd-upload-timeout`）
- 不推荐长期维护的 `dev` 分支——本项目规模较小，所有 PR 直接合入 `main` 即可

## 文档与版本号

- 重要变更（新增功能、Bug 修复、破坏性改动）需要在 `CHANGELOG.md` 中记录
- 版本号统一由根目录 [VERSION](file:///d:/GitHub/test/VERSION) 文件管理，**禁止在代码中硬编码版本号**
- README 中如有示例命令、依赖表、脚本列表变更，需同步更新

## 开发环境

```bash
# 克隆仓库
git clone https://github.com/tsy1102/a-stock-data.git
cd a-stock-data

# 安装运行依赖
pip install -r requirements.txt

# 安装开发依赖（pytest / mypy / black）
pip install -r requirements-dev.txt

# 提交前自检
black .
python -m mypy stock_common/ gd_uploader.py tdx_client.py --ignore-missing-imports
pytest tests/ -v
```

## 常见问题

- **如何更新节假日数据？**
  运行 `python scripts/update_calendar.py`，从 `chinese-calendar` 库拉取最新节假日并写入 `stock_common/stock_calendar.py`。可加 `--check` 仅查看支持年份范围。

- **缓存失效怎么办？**
  临时方案：设置环境变量 `STOCK_NOCACHE=1`
  永久清理：`python scripts/clean_cache.py`（清空全部）或 `python scripts/clean_cache.py --category <分类名>`

- **Google Drive 上传失败？**
  1) 删除 `credentials.json` 重新走 OAuth 流程；
  2) 确认 `client_secrets.json` 来自对应的 GCP 项目；
  3) 如根目录出现奇怪的个股文件夹，详见 `README.md` FAQ 章节。

---

感谢你的参与，让我们一起让 A 股分析更好用！ 🎉
