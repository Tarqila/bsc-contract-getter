---
name: bsc-contract-getter
description: 从 Etherscan V2 API 批量拉取 BSC 链合约源码与 ABI。Use when you need to download/verify contract source code or ABI for BSC (chainid 56) addresses, check if on-chain verified source changed, or archive contract code with version/date labels.
---

# Contract Getter(BSC 合约源码/ABI 下载)

基于 `scripts/fetch_contracts.py` 封装:按地址批量拉取合约源码 + ABI,按地址分目录保存。

## 首次设置

1. 到 <https://etherscan.io/apis> 申请一个免费 API key(免费档即支持 BSC)
2. 在脚本同目录创建 `.env` 文件:

```
ETHERSCAN_API_KEY=你的key
```

脚本启动时自动加载 `.env`,也支持直接读系统环境变量。

## 用法

```bash
cd scripts
python3 fetch_contracts.py --addresses 0xADDRESS1 0xADDRESS2 --output <输出目录>
```

输出结构:`<输出目录>/<地址>/abi.json + 按原始路径展开的源码文件`

依赖:Python 3.x + `requests`(`pip install requests`)

## API Key(免费档)

- 免费 key 实测支持 BSC(chainid=56)的 `getsourcecode` / `getabi`
- 免费档有调用频率限制(约 5 次/秒),批量拉取时地址间自行加 0.3s 以上间隔(脚本内可改)

## 网络要求

- 多数环境 api.etherscan.io 与公共 RPC 直连可用
- 若超时/拒绝连接,走代理重试:

```bash
export HTTPS_PROXY=http://127.0.0.1:7890  # 按实际代理端口
```

## 已知限制

- 脚本默认 BSC:`CHAIN_ID` 环境变量默认 56;如需以太坊主网在 .env 改 `CHAIN_ID=1`(免费 key 对主网同样可用,其他 L2 链需实测)
- 返回的源码可能是 standard-json / flat JSON / `// File:` 三种格式之一,脚本均可解析
- 未验证合约返回 `SourceCode` 为空,脚本会跳过(可用 Etherscan 返回的 `Proxy` / `Implementation` 字段识别代理实现关系)
- 公共 RPC 直读 ERC1967 实现槽可能返回 0(节点限制),代理实现以 Etherscan metadata 的 `Implementation` 字段为准
