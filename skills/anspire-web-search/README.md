# Anspire Web Search for OpenClaw

通过 Anspire Search API 为代理提供实时网页搜索能力。

## 能力概览

- 为 OpenClaw 增加实时联网搜索能力
- 适合处理最新新闻、时事、政策变化、市场动态等时效性问题
- 只依赖 `curl` 和环境变量 `ANSPIRE_API_KEY`
- 要求模型在失败时明确降级，不伪造实时结果

## 仓库结构

```text
README.md                  # README
```

## 通过 ClawHub 安装

用户可以执行：

```bash
clawhub install anspire-web-search
export ANSPIRE_API_KEY="你的 API Key"
```

然后重新开启一个 OpenClaw 会话，让技能加载器识别工作区下的 `skills/` 目录。

## 通过 GitHub 手动安装

```bash
mkdir -p ./skills/anspire-web-search
cp -R ./skill/* ./skills/anspire-web-search/
export ANSPIRE_API_KEY="你的 API Key"
```

然后重新开启 OpenClaw 会话。


