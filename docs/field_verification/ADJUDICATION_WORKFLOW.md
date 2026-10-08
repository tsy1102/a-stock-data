# 碰撞候选人工定案与注册表同步

`collide.py` 只发现候选，不直接改变主字典。只有经过人工核对的决定，才能通过此流程写入逐源字段注册表。数值命中本身不是语义定案。

## 可以进入此流程的候选

- 报告必须是 `collision_mode: verified_anchor_only`，且 `exploratory_pair_count` 为 0。
- 仅接受报告 `L1` 列表中的 `L1` 或 `L1-U` 候选；L4、方法候选和未知字段互撞结果不能直接晋级。
- `target` 必须精确对应报告 `left` 的运行时别名和完整字段路径，状态只能是 `unverified` 或 `candidate`。
- `anchor` 必须精确对应报告 `right`，并且注册表状态为 `verified`、来源谱系确认独立且允许作锚。若运行时别名映射到多个字典来源，决策文件必须明确指出正确的来源名。
- `conflict`、`disproved` 和现有 `verified` 字段不能由这条流程覆盖；状态冲突需要单独复核。

## 准备决策文件

复制 `docs/field_verification/adjudications/template.json` 到同目录的新文件。填写碰撞报告路径、复核人、复核日期和决定。报告路径相对于 `docs/field_verification/`；`target` / `anchor` 的 `code` 使用注册表中的完整路径。

工具目前只接受 `verify`：必须填写稳定的 `canonical`、明确的 `meaning` 和复核理由；`unit` 可为空，但不能猜测。只有确认目标与锚字段语义等价后才提交决定。无法证明等价时，不提交定案；目标字段保持原状态。单个碰撞对不等价不代表目标字段本身已被证伪。

## 预览和应用

在仓库根目录运行：

```powershell
python.exe scripts\apply_collision_adjudications.py --decisions docs\field_verification\adjudications\YYYYMMDD_review.json
```

预览会验证报告、完整字段身份、来源谱系和决定内容，不写文件。检查预览无误后，显式应用：

```powershell
python.exe scripts\apply_collision_adjudications.py --decisions docs\field_verification\adjudications\YYYYMMDD_review.json --apply
```

应用会以事务式写入更新 `field_registry.json`、兼容聚合字段状态和 `meta.source_field_stats`，并重生成 `field_dict.md`、`unknown_fields.md`、`source_repository_map.md`、`field_metadata_gaps.md`。验证记录会保留报告路径、样本日期、命中情况、复核人、决定理由和唯一决定 ID。确认等价的字段对还会写入 `mappings`，供后续碰撞跳过已定案关系；使用现有关系值 `same_number_same_meaning`。

`field_matrix.md` 表达字段和来源的覆盖关系，状态/语义变更不改变该投影。应用后仍应运行 `registry_parity.py`、`verify_sync_check.py` 和对应测试。

## GitHub 仓库确认状态

`source_lineage.json` 将本地项目证据状态 `repository_mapping_status` 与用户对话确认 `dialog_confirmation.status` 分开记录。用户确认某仓库是客户端、传输层或包装库，不会自动把它标成底层数据提供方，也不会改变独立来源族。来源映射页分别显示这两种状态；未确认条目保持 pending，取得候选仓库证据后再逐项与用户确认。
