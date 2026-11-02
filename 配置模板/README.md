# 接班配置

优先在工作台网页中保存配置，避免手改 JSON。首启会自动恢复脱敏的旧设置；模板供核对字段，不会自动覆盖正在使用的配置。

- `settings.example.json`：provider、base_url、model、search_provider、profile 及空的 api_key/tavily_api_key/notes_path。真实配置只保存在 `文案助手/wechat-writer/data/settings.json`。
- `coze_secrets.example.json`：topics 与 writer 的 base_url/token 空字段。先在网页保存对应部署地址，再填写该部署的接班 Token；旧地址和缓存 schema 已在业务数据库中。真实凭据只保存在 `data/coze_secrets.json`。

模型可选 Codex CLI、Ollama、本地或云端 OpenAI 兼容接口。当前继承模型名称为 `gpt-6-astra`，是否可用由接班账户决定。Codex 使用接班人的 CLI 登录；个人账号登录文件没有打包。Ollama 需要本机运行服务和已安装模型；云端兼容接口需要可用 base URL、模型名称与新 API key。

Tavily 用于文章/图片搜索；未填 API key 时程序尝试免密模式，可能遇到额度或网络限制，失败会显示真实错误。

Coze 扣子编程工作流部署要求 `https://子域.coze.site` 基址。程序先读取 `/graph_parameter`，提交一次 `/async_run`，查询 `/task/{task_id}`。接班需项目/工作空间权限、部署状态、额度及新的角色 Token。不要以预览链接代替 API 地址。缓存的 writer 参数有 `task_mode=export_library`，但这仅说明云端有案例库导出分支，不代表工作流源码可导出或现数据已导出；请在 Coze 项目中核对后操作。
