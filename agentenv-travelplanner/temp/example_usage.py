#!/usr/bin/env python3
"""
TravelPlanner Environment Usage Example
"""

import asyncio
import json
import httpx
import time


class TravelPlannerClient:
    """TravelPlanner 环境客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    async def create_environment(self) -> int:
        """创建新环境"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/create")
            response.raise_for_status()
            return response.json()["id"]
    
    async def reset_environment(self, env_id: int, query_id: int = 0) -> dict:
        """重置环境"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/reset",
                json={"env_idx": env_id, "query_id": query_id}
            )
            response.raise_for_status()
            return response.json()
    
    async def step(self, env_id: int, action: str) -> dict:
        """执行步骤"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/step",
                json={"env_idx": env_id, "action": action}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_info(self, env_id: int) -> dict:
        """获取环境信息"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/info?env_idx={env_id}")
            response.raise_for_status()
            return response.json()
    
    async def health_check(self) -> dict:
        """健康检查"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()


async def basic_usage_example():
    """基础使用示例"""
    print("=== TravelPlanner Environment Basic Usage Example ===\n")
    
    client = TravelPlannerClient()
    
    try:
        # 健康检查
        print("1. Health check...")
        health = await client.health_check()
        print(f"   Status: {health['status']}")
        
        # 创建环境
        print("\n2. Creating environment...")
        env_id = await client.create_environment()
        print(f"   Created environment with ID: {env_id}")
        
        # 重置环境
        print("\n3. Resetting environment...")
        reset_result = await client.reset_environment(env_id, query_id=0)
        print(f"   Initial state: {reset_result['state'][:200]}...")
        
        # 执行一系列动作
        actions = [
            'Action: FlightSearch with Action Input: {"departure_city": "New York", "destination_city": "Paris", "date": "2024-06-01"}',
            'Action: AccommodationSearch with Action Input: {"city": "Paris"}',
            'Action: NotebookWrite with Action Input: {"content": "Found good flight and hotel options for Paris trip"}',
            'Action: AttractionSearch with Action Input: {"city": "Paris"}',
            'Action: RestaurantSearch with Action Input: {"city": "Paris", "cuisine": "French"}',
            'Action: Planner with Action Input: {"query": "Create a comprehensive 5-day travel plan to Paris"}'
        ]
        
        print("\n4. Executing actions...")
        for i, action in enumerate(actions, 1):
            print(f"\n   Step {i}: {action[:60]}...")
            result = await client.step(env_id, action)
            print(f"   Reward: {result['reward']:.2f}, Done: {result['done']}")
            print(f"   Result: {result['state'][:150]}...")
            
            if result['done']:
                print("   Task completed!")
                break
            
            # 短暂延迟
            await asyncio.sleep(0.5)
        
        # 获取最终信息
        print("\n5. Getting final environment info...")
        info = await client.get_info(env_id)
        print(f"   Total steps: {info['info']['step_count']}")
        print(f"   Notebook entries: {len(info['info']['notebook_content'])}")
        
    except Exception as e:
        print(f"Error: {e}")


async def interactive_example():
    """交互式示例"""
    print("\n=== TravelPlanner Environment Interactive Example ===\n")
    
    client = TravelPlannerClient()
    
    try:
        # 创建环境
        env_id = await client.create_environment()
        print(f"Created environment {env_id}")
        
        # 重置环境
        reset_result = await client.reset_environment(env_id)
        print(f"\nInitial Query: {reset_result['info']['query']}")
        print("\nYou can now interact with the environment!")
        print("Available tools: FlightSearch, AccommodationSearch, RestaurantSearch, AttractionSearch")
        print("Example action: Action: FlightSearch with Action Input: {\"departure_city\": \"Tokyo\", \"destination_city\": \"Osaka\", \"date\": \"2024-07-15\"}")
        print("\nType 'quit' to exit\n")
        
        while True:
            # 获取用户输入
            action = input("Enter action: ").strip()
            
            if action.lower() == 'quit':
                break
            
            if not action:
                continue
            
            try:
                # 执行动作
                result = await client.step(env_id, action)
                
                print(f"\nReward: {result['reward']:.2f}")
                print(f"Done: {result['done']}")
                print(f"Response:\n{result['state']}\n")
                
                if result['done']:
                    print("Task completed!")
                    break
                    
            except Exception as e:
                print(f"Error executing action: {e}\n")
        
    except Exception as e:
        print(f"Error: {e}")


async def stress_test_example():
    """压力测试示例"""
    print("\n=== TravelPlanner Environment Stress Test ===\n")
    
    client = TravelPlannerClient()
    num_environments = 5
    
    try:
        print(f"Creating {num_environments} environments...")
        
        # 创建多个环境
        env_ids = []
        for i in range(num_environments):
            env_id = await client.create_environment()
            env_ids.append(env_id)
            print(f"   Created environment {env_id}")
        
        # 并发执行动作
        print(f"\nExecuting actions in parallel...")
        
        async def run_environment(env_id, query_id):
            # 重置环境
            await client.reset_environment(env_id, query_id)
            
            # 执行几个动作
            actions = [
                'Action: FlightSearch with Action Input: {"departure_city": "Tokyo", "destination_city": "Seoul", "date": "2024-08-01"}',
                'Action: AccommodationSearch with Action Input: {"city": "Seoul"}',
                'Action: Planner with Action Input: {"query": "Create travel plan"}'
            ]
            
            total_reward = 0
            for action in actions:
                result = await client.step(env_id, action)
                total_reward += result['reward']
                
                if result['done']:
                    break
            
            return env_id, total_reward
        
        # 并发运行
        tasks = [run_environment(env_id, i) for i, env_id in enumerate(env_ids)]
        results = await asyncio.gather(*tasks)
        
        print("\nResults:")
        for env_id, total_reward in results:
            print(f"   Environment {env_id}: Total reward = {total_reward:.2f}")
            
    except Exception as e:
        print(f"Error: {e}")


def main():
    """主函数"""
    print("TravelPlanner Environment Usage Examples")
    print("========================================")
    
    print("\nAvailable examples:")
    print("1. Basic usage example")
    print("2. Interactive example") 
    print("3. Stress test example")
    
    choice = input("\nEnter choice (1-3) or 'all' for all examples: ").strip()
    
    if choice == '1' or choice == 'all':
        asyncio.run(basic_usage_example())
    
    if choice == '2':
        asyncio.run(interactive_example())
    
    if choice == '3' or choice == 'all':
        asyncio.run(stress_test_example())
    
    if choice not in ['1', '2', '3', 'all']:
        print("Invalid choice. Running basic example...")
        asyncio.run(basic_usage_example())


if __name__ == "__main__":
    main() 