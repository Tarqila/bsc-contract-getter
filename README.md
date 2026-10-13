# bsc-contract-getter

基于 Etherscan V2 API 的命令行小工具（亦可用作 AI Agent Skill）：按地址批量拉取 BSC 链合约的已验证源码与 ABI，按地址分目录保存，方便合约审计、代码归档与取证。

## 功能

- 批量拉取多个合约地址的源码 + ABI
- 按地址分目录保存，源码按原始路径展开
- 支持 standard-json / flat JSON / `// File:` 三种源码格式，均可自动解析
- 默认 BSC（chainid 56），改一个环境变量即可切换到其他 EVM 链

## 环境要求

- Python 3.x
- `requests`：`pip install requests`

## 1. 申请 API Key

到 Etherscan 官网 <https://etherscan.io/apis> 注册并申请免费 API key（免费档即可支持 BSC）。

## 2. 配置 API Key

在 `scripts/` 目录下创建 `.env` 文件：

```
ETHERSCAN_API_KEY=你的key
```

脚本启动时自动加载 `.env`，也支持直接读系统环境变量。

> `.env` 已在 `.gitignore` 中，不会提交到仓库；自己的 key 请勿提交或泄露。

## 3. 使用

```bash
cd scripts
python3 fetch_contracts.py --addresses 0xADDRESS1 0xADDRESS2 --output <输出目录>
```

输出结构：

```
<输出目录>/
├── 0xContractAddress1/
│   ├── abi.json
│   └── contracts/...        # 按原始路径展开的源码
└── 0xContractAddress2/
    ├── abi.json
    └── contract.sol
```

## 切换到其他链（修改 Chain ID）

脚本默认 BSC（chainid = 56）。在 `.env` 中加一行即可切换：

```
CHAIN_ID=1
```

常用 chainid 参考（Etherscan V2 统一接口）：

| 链 | chainid |
|---|---|
| BSC（默认） | 56 |
| Ethereum | 1 |
| Polygon | 137 |
| Arbitrum One | 42161 |
| Optimism | 10 |
| Base | 8453 |

注意：免费 key 实测 BSC / 以太坊主网可用；其他链能否使用取决于 Etherscan 对该链的免费策略，请自行实测。

## 网络说明

- 多数环境 `api.etherscan.io` 直连可用
- 若超时/被拒，走代理重试：`export HTTPS_PROXY=http://127.0.0.1:7890`（按实际代理端口修改）

## 已知限制

- 免费档有调用频率限制（约 5 次/秒），批量拉取时注意控制请求频率
- 未验证合约 `SourceCode` 为空，脚本会跳过（可用 Etherscan 返回的 `Proxy` / `Implementation` 字段识别代理实现关系）
- 公共 RPC 直读 ERC1967 实现槽可能返回 0，代理实现以 Etherscan metadata 的 `Implementation` 字段为准

## 目录结构

```
bsc-contract-getter/
├── README.md
├── SKILL.md                  # Skill 描述（可被 AI Agent 加载）
└── scripts/
    └── fetch_contracts.py
```

## 许可证（License）

保留所有权利（All Rights Reserved），自定义授权如下：

- **个人学习、研究、自用：免费，无需授权。**
- **任何商用平台的转载、集成、二次开发及盈利行为，必须：① 注明来源（本仓库链接）；② 事先获得商业授权。**

本声明旨在保留原作者版权与商业权利，防止代码被滥用。如需商业授权，请联系本人。

Copyright © 2026 nigel（GitHub: Tarqila）
