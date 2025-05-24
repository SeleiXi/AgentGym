# TravelPlanner Environment for AgentGym

这个包为 AgentGym 提供了 TravelPlanner 基准测试环境的兼容包装器，使语言智能体能够处理复杂的旅行规划任务，包括工具使用和约束满足。

## 🎯 概述

TravelPlanner 是一个用于评估语言智能体在真实世界规划场景中的基准测试。此环境包装器允许智能体：

- **使用旅行工具**: 搜索航班、住宿、餐厅、景点并计算距离
- **生成计划**: 创建全面的多日旅行行程
- **处理约束**: 满足常识和硬约束（预算、偏好等）
- **获得评估**: 根据约束满足度指标评估计划

## 🚀 快速开始

### 安装

```bash
# 克隆或导航到 TravelPlanner 环境目录
conda create -n agentenv-travelplanner python==3.12

conda activate agentenv-travelplanner

cd agentenv-travelplanner

# 安装依赖
pip install -r requirements.txt

```

### 启动服务器

```bash
# 使用默认设置启动服务器
python -m agentenv_travelplanner.launch

# 或使用自定义参数
python -m agentenv_travelplanner.launch --host 0.0.0.0 --port 8000 --log-level info

# 使用安装的命令行工具
travelplanner-env --port 8001
```

### API 使用

服务器启动后，您可以通过 HTTP API 与环境交互：

#### 基础 API 端点

```bash
# 健康检查
GET http://localhost:8000/health

# 创建新环境
POST http://localhost:8000/create

# 重置环境
POST http://localhost:8000/reset
{
  "env_idx": 0,
  "query_id": 0
}

# 执行动作
POST http://localhost:8000/step
{
  "env_idx": 0,
  "action": "Action: FlightSearch with Action Input: {\"departure_city\": \"New York\", \"destination_city\": \"Paris\", \"date\": \"2024-06-01\"}"
}

# 获取环境信息
GET http://localhost:8000/info?env_idx=0
```

## 🛠️ 可用工具

1. **FlightSearch**: 查找特定日期城市间的航班
2. **AccommodationSearch**: 发现酒店和住宿选择
3. **RestaurantSearch**: 按菜系类型查找餐饮选择
4. **AttractionSearch**: 定位旅游景点和活动
5. **GoogleDistanceMatrix**: 计算旅行距离和时间
6. **CitySearch**: 查找州/地区内的城市
7. **NotebookWrite**: 保存收集的规划信息
8. **Planner**: 生成最终的结构化旅行计划

## 📋 使用示例

### Python 客户端示例

```python
import asyncio
import httpx

async def example():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 创建环境
        response = await client.post(f"{base_url}/create")
        env_id = response.json()["id"]
        
        # 重置环境
        await client.post(f"{base_url}/reset", 
                         json={"env_idx": env_id, "query_id": 0})
        
        # 执行动作
        action = 'Action: FlightSearch with Action Input: {"departure_city": "Tokyo", "destination_city": "Osaka", "date": "2024-07-15"}'
        response = await client.post(f"{base_url}/step",
                                   json={"env_idx": env_id, "action": action})
        
        result = response.json()
        print(f"Reward: {result['reward']}, Done: {result['done']}")
        print(f"State: {result['state']}")

asyncio.run(example())
```

### 动作格式

动作应遵循以下格式：
```
Action: [工具名] with Action Input: [JSON参数]
```

#### 示例动作:

```python
# 搜索航班
"Action: FlightSearch with Action Input: {\"departure_city\": \"New York\", \"destination_city\": \"Paris\", \"date\": \"2024-06-01\"}"

# 查找住宿
"Action: AccommodationSearch with Action Input: {\"city\": \"Paris\"}"

# 生成计划
"Action: Planner with Action Input: {\"query\": \"为2人制定为期5天的巴黎之旅，预算3000美元\"}"
```

## 🗃️ 数据集

环境使用来自 HuggingFace 的 TravelPlanner 数据集：
- **训练集**: 45个查询
- **验证集**: 180个查询
- **测试集**: 1000个查询

每个查询包括：
- 自然语言旅行需求
- 难度级别（简单/中等/困难）
- 旅行持续时间（3/5/7天）
- 本地约束（预算、偏好）

## 📁 环境结构

```
agentenv-travelplanner/
├── agentenv_travelplanner/        # Python 包
│   ├── __init__.py               # 包初始化
│   ├── server.py                 # FastAPI 服务器
│   ├── model.py                  # Pydantic 模型
│   ├── environment.py            # 环境实现
│   ├── launch.py                # 启动脚本
│   ├── utils.py                  # 工具函数
│   └── config.yaml               # 配置文件
├── TravelPlanner/                 # 原始 TravelPlanner 代码库
├── requirements.txt              # 依赖规范
├── setup.py                      # 安装脚本
├── example_usage.py              # 使用示例
├── test_environment.py           # 测试文件
└── README.md                     # 此文件
```

## 🔧 配置

编辑 `agentenv_travelplanner/config.yaml` 来自定义：
- 模型设置
- 工具配置
- 评估参数
- 服务器设置

## 🧪 测试

运行测试以验证环境：

```bash
# 运行基础测试
python test_environment.py

# 使用 pytest（如果已安装）
pytest test_environment.py -v

# 运行使用示例
python example_usage.py
```

## 🚧 当前限制

1. **模拟实现**: 当前版本由于数据库设置复杂性使用模拟工具响应
2. **简化评估**: 使用启发式评估而非完整约束检查
3. **有限工具集成**: 工具是模拟的而非完全功能性的
4. **数据库设置**: 需要手动数据库下载和配置

## 🔮 未来改进

1. **完整数据库集成**: 设置完整的旅行数据库
2. **真实工具实现**: 实现实际的工具 API
3. **高级评估**: 集成完整的 TravelPlanner 评估系统
4. **服务器架构**: 为分布式使用添加环境服务器
5. **增强奖励**: 更复杂的奖励塑造
6. **工具学习**: 支持有效学习使用工具

## 🤝 与 AgentGym 的集成

此环境遵循 AgentGym 模式：

- **FastAPI 服务器**: 通过 HTTP API 处理环境交互
- **标准化端点**: 创建、重置、步骤、信息 API
- **结构化通信**: 使用 Pydantic 模型进行请求/响应
- **错误处理**: 强大的错误处理和日志记录

该环境可以与任何兼容 AgentGym 的训练框架一起使用。

## 📄 许可证

此环境包装器在与原始 TravelPlanner 项目相同的许可证下提供。

## 📖 引用

如果您使用此环境，请引用：

```bibtex
@inproceedings{xie2024travelplanner,
  title={TravelPlanner: A Benchmark for Real-World Planning with Language Agents},
  author={Xie, Jian and Zhang, Kai and Chen, Jiangjie and Zhu, Tinghui and Lou, Renze and Tian, Yuandong and Xiao, Yanghua and Su, Yu},
  booktitle={Forty-first International Conference on Machine Learning},
  year={2024}
}
``` 