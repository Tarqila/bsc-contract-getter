import requests
import json
import os
import argparse
import sys

def load_env_file(env_path=".env"):
    """从 .env 文件加载环境变量"""
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print(f"Warning: {env_path} file not found. Using default values or system environment variables.")

def print_directory_tree(path, prefix=""):
    """打印目录结构"""
    if not os.path.exists(path):
        return
    
    entries = sorted(os.listdir(path))
    directories = []
    files = []
    
    for entry in entries:
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            directories.append(entry)
        else:
            files.append(entry)
    
    # 先打印文件
    for file in files:
        print(f"{prefix}├── {file}")
    
    # 再打印目录
    for i, directory in enumerate(directories):
        directory_path = os.path.join(path, directory)
        is_last = i == len(directories) - 1
        
        print(f"{prefix}├── {directory}/")
        
        new_prefix = f"{prefix}│   " if not is_last else f"{prefix}    "
        print_directory_tree(directory_path, new_prefix)

# 加载环境变量
load_env_file()

# 从环境变量读取配置
API_KEY = os.environ.get("ETHERSCAN_API_KEY", "")
API_BASE_URL = os.environ.get("ETHERSCAN_API_URL", "https://api.etherscan.io/v2/api")
CHAIN_ID = os.environ.get("CHAIN_ID", "56")

def get_contract_source_code(address):
    """获取合约源码"""
    params = {
        "chainid": CHAIN_ID,
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": API_KEY
    }
    try:
        response = requests.get(API_BASE_URL, params=params, timeout=10)
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.text}")
        data = response.json()
        
        print(f"API Status: {data.get('status')}")
        print(f"API Message: {data.get('message')}")
        
        if data.get("status") == "1" and len(data.get("result", [])) > 0:
            result = data["result"][0]
            return {
                "source": result.get("SourceCode", ""),
                "contract_name": result.get("ContractName", ""),
                "compiler_version": result.get("CompilerVersion", ""),
                "optimization": result.get("OptimizationUsed", ""),
                "runs": result.get("Runs", ""),
                "constructor_arguments": result.get("ConstructorArguments", ""),
                "evm_version": result.get("EVMVersion", ""),
                "library": result.get("Library", ""),
                "license_type": result.get("LicenseType", ""),
                "proxy": result.get("Proxy", ""),
                "implementation": result.get("Implementation", ""),
                "swarm_source": result.get("SwarmSource", "")
            }
        return None
    except Exception as e:
        print(f"Error fetching source code: {str(e)}")
        return None

def get_contract_abi(address):
    """获取合约ABI"""
    params = {
        "chainid": CHAIN_ID,
        "module": "contract",
        "action": "getabi",
        "address": address,
        "apikey": API_KEY
    }
    try:
        response = requests.get(API_BASE_URL, params=params, timeout=10)
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.text}")
        data = response.json()
        
        print(f"API Status: {data.get('status')}")
        print(f"API Message: {data.get('message')}")
        
        if data.get("status") == "1":
            return data.get("result", "")
        return None
    except Exception as e:
        print(f"Error fetching ABI: {str(e)}")
        return None

def parse_source_code(source_code):
    """解析合约源码，提取文件路径和内容"""
    files = {}
    
    # 处理标准格式的源码（包含文件路径的JSON格式）
    if source_code.startswith("{"):
        try:
            source_dict = json.loads(source_code)
            for file_path, content in source_dict.items():
                # 将文件路径中的反斜杠转换为正斜杠
                normalized_path = file_path.replace("\\", "/")
                files[normalized_path] = content
            return files
        except json.JSONDecodeError:
            # 如果不是有效的JSON，继续尝试其他格式
            pass
    
    # 处理包含 // File: 注释分隔的格式
    lines = source_code.split('\n')
    current_file_path = None
    current_content = []
    
    for line in lines:
        # 检查是否是文件分隔符注释
        if line.startswith("// File:"):
            # 如果之前有文件内容，先保存
            if current_file_path is not None and current_content:
                files[current_file_path] = '\n'.join(current_content)
            
            # 提取新文件路径
            file_path = line[len("// File:"):].strip()
            # 将反斜杠转换为正斜杠
            current_file_path = file_path.replace("\\", "/")
            current_content = []
        elif current_file_path is not None:
            current_content.append(line)
    
    # 保存最后一个文件
    if current_file_path is not None and current_content:
        files[current_file_path] = '\n'.join(current_content)
    
    # 如果没有找到任何文件分隔符，返回原始内容作为单个文件
    if not files:
        files["contract.sol"] = source_code
    
    return files

def save_contract_files(base_dir, address, source_files, abi):
    """保存合约文件到本地目录"""
    # 创建以合约地址命名的主文件夹
    contract_dir = os.path.join(base_dir, address)
    os.makedirs(contract_dir, exist_ok=True)
    
    # 保存ABI文件
    if abi:
        abi_path = os.path.join(contract_dir, "abi.json")
        with open(abi_path, "w", encoding="utf-8") as f:
            f.write(abi)
        print(f"ABI saved to: {abi_path}")
    
    # 保存源码文件
    for file_path, content in source_files.items():
        # 创建完整的文件路径
        full_path = os.path.join(contract_dir, file_path)
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        # 写入文件
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Source code saved to: {full_path}")

def fetch_contracts(contract_addresses, save_dir):
    """批量获取合约源码和ABI"""
    for address in contract_addresses:
        address = address.strip()
        print(f"\nFetching contract: {address}")
        
        # 获取源码
        source_data = get_contract_source_code(address)
        if not source_data:
            print(f"Failed to get source code for {address}")
            continue
        
        # 解析源码
        source_files = parse_source_code(source_data["source"])
        
        # 获取ABI
        abi = get_contract_abi(address)
        if not abi:
            print(f"Failed to get ABI for {address}")
        
        # 保存文件
        save_contract_files(save_dir, address, source_files, abi)
        
        print(f"Successfully fetched contract: {address}")

def generate_readme(output_dir):
    """生成 README 文件"""
    readme_content = """# Contract Source Code Fetcher

This script fetches Ethereum/Binance Smart Chain contract source code and ABI using Etherscan API.

## Features

- Batch fetch multiple contracts at once
- Preserve original directory structure from deployment
- Save both source code and ABI
- Auto-generate directory structure visualization

## Usage

```bash
python3 fetch_contracts.py --addresses <contract_address1> <contract_address2> ... --output <output_directory>
```

### Example

```bash
# Fetch a single contract
python3 fetch_contracts.py --addresses 0xa2f464A2462AEd49B9b31eB8861bC6B0BBb0483F --output ./contracts

# Fetch multiple contracts
python3 fetch_contracts.py --addresses 0xa2f464A2462AEd49B9b31eB8861bC6B0BBb0483F 0x72212F35aC448FE7763aA1BFdb360193Fa098E52 --output ./contracts
```

## Arguments

- `--addresses`: One or more contract addresses to fetch (required)
- `--output`: Directory to save the contracts (required)

## Output Structure

```
output_directory/
├── 0xContractAddress1/
│   ├── abi.json
│   └── contracts/
│       ├── interfaces/
│       │   └── IContract.sol
│       └── Contract.sol
└── 0xContractAddress2/
    ├── abi.json
    └── contract.sol
```

## Notes

- This script uses Binance Smart Chain (chainid=56) by default
- You need an Etherscan API key to use this script
- API rate limits apply, be mindful of request frequency

## Requirements

- Python 3.x
- requests library

Install dependencies:
```bash
pip install requests
```
"""
    
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"README.md saved to: {readme_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Batch fetch Ethereum contract source code and ABI")
    parser.add_argument("--addresses", nargs="+", required=True, help="Contract addresses to fetch")
    parser.add_argument("--output", required=True, help="Directory to save the contracts")
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output, exist_ok=True)
    
    # 批量获取合约
    fetch_contracts(args.addresses, args.output)
    
    # 打印目录结构
    print("\n" + "="*60)
    print("Generated Directory Structure:")
    print("="*60)
    print(f"./{os.path.basename(args.output)}/")
    print_directory_tree(args.output, "    ")

if __name__ == "__main__":
    main()
