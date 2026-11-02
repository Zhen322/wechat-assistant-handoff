# 交接数据快照与恢复

本目录以原项目 `backup.py` 的 SQLite 在线备份为基础，并对采集内容中已识别的私人联系邮箱、手机号做公开脱敏，日期见 [snapshot-manifest.json](snapshot-manifest.json)。导出文件与数据库保留相同的完整记录集合，并同步替换联系信息；它们是公开交接派生版本，不是原文件的字节副本。数据库已整理为单文件（journal_mode=DELETE），不依赖 WAL/SHM。它是只读交接基线，运行中的数据库在 `文案助手/wechat-writer/data/`。

## 数据清单

| 数据 | 数量 | 直接阅读 |
| --- | ---: | --- |
| 素材 | 12（7 全文、5 摘要） | [articles](data/articles/) |
| 写法卡 | 5（1 已批准） | [cards](data/cards/) |
| 草稿 | 4 | [drafts](data/drafts/) |
| 执行任务 | 15 | SQLite jobs 表；Coze 结果另见 [coze](data/coze/) |
| B 写作流程 | 3 | [writing](data/writing/) |
| 选题批次 | 1（5 候选） | [topics](data/topics/) |
| Coze 配置 | 2 | [公共配置及接口合同](data/coze/public-config.json) |
| 发布复盘 | 0 | SQLite performance_records 表 |

[用户笔记](data/notes/我的思考.md) 与 [当前写作规范](data/writing-policy/) 已收录。settings.json 的模型/API/Tavily 密钥为空，notes_path 为空（使用项目内笔记），Coze secrets 文件未收录。数据库保留已有任务的错误和待审状态。

## 恢复

最简单方式：在仓库根目录运行 `python3 start.py`，首次自动恢复，然后启动服务。

只恢复不启动：

```sh
python3 restore-data.py
```

若目标已有 `workspace.sqlite3`，脚本返回失败并保持原数据库不变。已有笔记、配置和其他同名文件也不会覆盖。需要单独恢复一个新副本时：

```sh
python3 restore-data.py --target /绝对路径/新的数据目录
```

之后用 `WECHAT_WRITER_DATA` 指向该目录运行根目录 start.py。macOS/Linux 示例：

```sh
WECHAT_WRITER_DATA=/绝对路径/新的数据目录 python3 start.py --port 8766
```

Windows PowerShell 示例：

```powershell
$env:WECHAT_WRITER_DATA = 'C:\workspace\新的数据目录'
py -3 start.py --port 8766
```

恢复脚本核对数据库 SHA-256、SQLite 完整性与表记录数，复制业务数据，并将草稿/卡片的输出路径改为新机器路径。历史证据快照中的旧路径作为来源记录保留。不要在另一个服务正在使用目标目录时恢复；不要用复制单个活动 SQLite 文件的方式替代在线快照。

## 保存后续工作

工作台的 `backup.command` 会生成带时间的新 ZIP，含当前数据库与可阅读全文，自动排除 Coze Token 并清空模型密钥。交接仓库的 `.gitignore` 排除运行中的数据库和密钥，防止意外提交；需要更新交接基线时应先生成新一致快照并检查，再替换本目录，重新计算 snapshot-manifest.json 中的数据库摘要。不要把自己的 API Token、Codex 登录文件放入仓库。
