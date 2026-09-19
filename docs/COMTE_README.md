# comte 加密配置文件 —— 项目内解密与核查说明

> 数据来源：通达信本地 `comte` 配置文件（行情主站列表）。仅做本地数据自解析，结论不构成投资建议。
> 算法详情与逆向过程见 [`ZHB_COMTE_ROUTEA_FINDINGS_20260919.md`](ZHB_COMTE_ROUTEA_FINDINGS_20260919.md)。

## 一、这是什么
`comte` 系列是通达信的**加密行情主站配置文件**（IP/端口/券商名），共 6 个：
`nacomte / nbcomte / nscomte / nscomte_std / nzcomte / nvcomte`。
它们不是市场数据字段文件，而是客户端连接行情服务器的地址簿。

## 二、算法（已实证）
```
comte = 16 字节私有文件头 (7a99696405d414671ba17a0587d9b86e) + N 字节载荷
载荷 = 逐字节异或的自同步流密码密文：C[i] = P[i] ^ KS_file[i]
```
- **非 AES-ECB/CBC**：6 文件载荷长度均非 16 整数倍（标准分组密文不可能）。
- **密钥流逐文件独立**（类 AES-CFB / 带密文反馈 PRNG）：KS 随此前密文演化，故
  仅公共前缀段（各文件 `[CooHost]` 三主站明文相同）密钥流重合，内容分叉后逐文件独立。
  不存在"一条全局密钥流解全部文件"。
- 密钥运行时派生，非静态存储（详报告 §3）。

## 三、项目内如何"随时解开阅读"
统一入口：`scripts/comte_decrypt.py`（自包含，Windows 下可捕获/离线解密/核查）。

产物固化于 `cache/zhb/comte/`（gitignore，本机持久），即"随时可读"的数据：
```
cache/zhb/comte/
├── <name>.dat                # 加密源（已复制到项目，自包含可选）
├── <name>.keystream.bin      # 该文件专属密钥流（解密金钥，逐文件）
├── <name>.decrypted.ini      # 解密后的可读明文（直接用记事本/任意工具打开即可）
└── VERIFY_REPORT.md          # 字段真实性核查报告
```
> 想读数据？直接打开 `<name>.decrypted.ini` 即可（GBK 编码的 INI，含 `[CooHost]` 等段与
> `HostName01=` / `IPAddress01=` / `Port01=` 等字段）。

### 子命令
```bash
# 1) 从运行中 TdxW.exe 内存捕获 6 文件专属密钥流（须先启动通达信）
python scripts/comte_decrypt.py capture

# 2) 用各自密钥流离线解密全部 6 文件 -> cache/zhb/comte/*.decrypted.ini
python scripts/comte_decrypt.py decrypt --all

# 3) 核查 6 文件字段真实性（解密 + 解析 INI + 断言；TdxW 在跑时复验内存==离线 0 差异）
python scripts/comte_decrypt.py verify
```
也可针对单个文件：`capture --dat <x.dat>` / `decrypt --dat <x.dat>`。

## 四、字段真实性核查结论 ✅
`verify` 已通过（详见 `cache/zhb/comte/VERIFY_REPORT.md`）：
- **铁证**：nacomte 运行时内存明文 == 离线解密，差异字节数 = 0 → 密钥流真实。
- 6 文件均用各自专属密钥流解密为真实可读 INI：

| 文件 | 段数 | 字段数 | readability |
|---|---|---|---|
| nacomte.dat | 8 | 347 | 0.992 |
| nbcomte.dat | 8 | 347 | 0.992 |
| nscomte.dat | 2 | 55 | 1.000 |
| nscomte_std.dat | 2 | 60 | 1.000 |
| nzcomte.dat | 2 | 100 | 1.000 |
| nvcomte.dat | 8 | 298 | 1.000 |

（nacomte/nbcomte 的 0.992 来自文件尾部固定宽度券商名二进制块 `银河证券`+NUL 填充，非损坏。）

## 五、刷新与维护
- 密钥流随用户服务器配置版本变化。**换服务器 / 升级通达信后**，重跑 `capture` 即可刷新
  全部专属密钥流并重新解密。
- `cache/` 被 gitignore：密钥流与明文二进制在本机持久（随时可读），但**不进 VCS**；
  如需跨机器复现，从已启动通达信的机器重跑 `capture` 即可（无需任何静态逆向）。

## 六、合规
本地二进制自解析研究，仅用于数据格式理解，不构成投资建议。
