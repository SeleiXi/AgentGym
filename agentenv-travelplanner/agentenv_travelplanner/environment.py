"""
TravelPlanner Environment Implementation
"""

import os
import sys
import json
import random
import logging
from typing import Dict, Any, List, Tuple, Optional
from datasets import load_dataset
# dataset: https://huggingface.co/datasets/osunlp/TravelPlanner
import yaml

# 添加 TravelPlanner 路径以导入工具
current_dir = os.path.dirname(os.path.abspath(__file__))
travelplanner_dir = os.path.join(current_dir, '..', 'TravelPlanner')
travelplanner_dir = os.path.abspath(travelplanner_dir)

# 确保 TravelPlanner 目录在 Python 路径中
if travelplanner_dir not in sys.path:
    sys.path.insert(0, travelplanner_dir)

# 添加子目录到路径
tools_dir = os.path.join(travelplanner_dir, 'tools')
agents_dir = os.path.join(travelplanner_dir, 'agents')
utils_dir = os.path.join(travelplanner_dir, 'utils')

for path in [tools_dir, agents_dir, utils_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

# 导入真实的工具类
from tools.flights.apis import Flights
from tools.accommodations.apis import Accommodations
from tools.restaurants.apis import Restaurants
from tools.attractions.apis import Attractions
from tools.googleDistanceMatrix.apis import GoogleDistanceMatrix
from tools.cities.apis import Cities
from tools.notebook.apis import Notebook
from tools.planner.apis import Planner  # 注释掉 planner 导入

# Mock工具实现保持不变以防需要
class MockFlights:
    def run(self, origin: str, destination: str, departure_date: str):
        return f"Mock flight from {origin} to {destination} on {departure_date}: Flight AA123, $299"

class MockAccommodations:
    def run(self, city: str):
        return f"Mock accommodation in {city}: Hotel ABC, $150/night"

class MockRestaurants:
    def run(self, city: str):
        return f"Mock restaurant in {city}: Restaurant XYZ, Italian cuisine, 4.5 stars"

class MockAttractions:
    def run(self, city: str):
        return f"Mock attraction in {city}: Famous Museum, 5 stars"

class MockDistanceMatrix:
    def run(self, origin: str, destination: str, mode: str = 'driving'):
        return f"Mock {mode} from {origin} to {destination}: 2 hours, 100 miles, $50"

class MockCities:
    def run(self, state: str):
        return [f"City1({state})", f"City2({state})", f"City3({state})"]

class MockNotebook:
    def __init__(self):
        self.data = []
    
    def write(self, input_data, short_description: str):
        self.data.append({"Short Description": short_description, "Content": input_data})
        return f"The information has been recorded in Notebook, and its index is {len(self.data)-1}."
    
    def list(self):
        return [{"index": i, "Short Description": item['Short Description']} for i, item in enumerate(self.data)]

# class MockPlanner:  # 注释掉 MockPlanner
#     def run(self, text: str, query: str):
#         return f"Mock plan for query: {query[:100]}..."

class TravelPlannerEnvironment:
    def __init__(self, use_real_tools: bool = True):
        self.use_real_tools = use_real_tools
        self.envs = {}
        self._max_id = 0  # 用于生成环境ID
        self.setup_tools()
        
    def setup_tools(self):
        """初始化工具"""
        if self.use_real_tools:
            try:
                # 使用真实的 TravelPlanner 工具
                print("Setting up real TravelPlanner tools...")
                self.flights = Flights()
                self.accommodations = Accommodations()
                self.restaurants = Restaurants()
                self.attractions = Attractions()
                self.distance_matrix = GoogleDistanceMatrix()
                self.cities = Cities()
                self.notebook = Notebook()
                self.planner = Planner()  # 注释掉 planner 初始化
                print("Real TravelPlanner tools setup complete.")
            except Exception as e:
                print(f"Failed to setup real tools, falling back to mock tools: {e}")
                self.setup_mock_tools()
        else:
            self.setup_mock_tools()
    
    def setup_mock_tools(self):
        """设置模拟工具"""
        print("Setting up mock tools...")
        self.flights = MockFlights()
        self.accommodations = MockAccommodations()
        self.restaurants = MockRestaurants()
        self.attractions = MockAttractions()
        self.distance_matrix = MockDistanceMatrix()
        self.cities = MockCities()
        self.notebook = MockNotebook()
        # self.planner = MockPlanner()  # 注释掉 mock planner
        print("Mock tools setup complete.")

    def create(self) -> int:
        """创建新的环境实例"""
        env_id = self._max_id
        self._max_id += 1
        
        # 在 envs 字典中创建环境占位符，这样 step 方法就不会报错
        self.envs[env_id] = {
            'query': '',
            'step_count': 0,
            'max_steps': 30,
            'history': [],
            'notebook_data': [],
            'use_react_agent': False,
            'done': False,
            'initialized': False,  # 标记环境是否已经通过 reset 初始化
            'agent_started': False,
            'agent_result': None,
            'agent_scratchpad': None
        }
        
        print(f"Created environment with ID: {env_id}")
        return env_id
    
    def list_environments(self) -> List[int]:
        """列出所有环境实例"""
        return list(self.envs.keys())

    def reset(self, env_idx: int, query: str, use_react_agent: bool = True) -> Dict[str, Any]:
        """重置环境状态"""
        # 确保环境存在
        if env_idx not in self.envs:
            return {
                'observation': 'Environment not found. Please create environment first.',
                'info': {'error': 'Environment not found'}
            }
            
        self.envs[env_idx] = {
            'query': query,
            'step_count': 0,
            'max_steps': 30,
            'history': [],
            'notebook_data': [],
            'use_react_agent': use_react_agent,
            'done': False,
            'initialized': True,  # 标记环境已经初始化
            'agent_started': False,
            'agent_result': None,
            'agent_scratchpad': None
        }
        
        if use_react_agent:
            try:
                # 使用真实的 ReactAgent
                from agents.tool_agents import ReactAgent
                
                # 构建正确的 citySet 文件路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                travelplanner_dir = os.path.join(current_dir, '..', 'TravelPlanner')
                city_file_path = os.path.join(travelplanner_dir, 'database', 'background', 'citySet_with_states.txt')
                city_file_path = os.path.abspath(city_file_path)
                
                # 创建一个临时的只包含城市名的文件，用于 ReactAgent
                temp_city_file = os.path.join(current_dir, 'temp_citySet.txt')
                try:
                    # 读取原始城市文件并提取城市名
                    with open(city_file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # 提取城市名（第一列），并创建临时文件
                    city_names = []
                    for line in lines:
                        if '\t' in line:
                            city_name = line.split('\t')[0].strip()
                            city_names.append(city_name)
                    
                    # 写入临时文件
                    with open(temp_city_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(city_names))
                    
                    # 使用临时文件路径
                    actual_city_file_path = temp_city_file
                    
                except Exception as e:
                    print(f"Failed to create temp city file, using original: {e}")
                    actual_city_file_path = city_file_path
                
                # 提供必要的参数，参考 tool_agents.py 第648行的用法
                self.envs[env_idx]['agent'] = ReactAgent(
                    args=None,  # 可以传递 None
                    tools=['flights', 'accommodations', 'restaurants', 'attractions', 'googleDistanceMatrix', 'cities', 'notebook', 'planner'],
                    max_steps=30,
                    react_llm_name='gpt-3.5-turbo-1106',
                    planner_llm_name='gpt-3.5-turbo-1106',
                    city_file_path=actual_city_file_path
                )
                return {
                    'observation': f'Environment reset successfully. Ready to plan: {query}',
                    'info': {'agent_type': 'real_react_agent'}
                }
            except Exception as e:
                print(f"Failed to create ReactAgent, using mock mode: {e}")
                return {
                    'observation': f'Environment reset successfully (mock mode). Ready to plan: {query}',
                    'info': {'agent_type': 'mock'}
                }
        else:
            return {
                'observation': f'Environment reset successfully. Ready to plan: {query}',
                'info': {'agent_type': 'direct_tools'}
            }

    def step(self, env_idx: int, action: str) -> Dict[str, Any]:
        """执行一步动作"""
        if env_idx not in self.envs:
            return {
                'observation': 'Environment not found. Please create environment first.',
                'reward': 0,
                'done': True,
                'info': {'error': 'Environment not found'}
            }
        
        env = self.envs[env_idx]
        
        # 检查环境是否已经通过 reset 初始化
        if not env.get('initialized', False):
            return {
                'observation': 'Environment not initialized. Please call reset first with a query.',
                'reward': 0,
                'done': True,
                'info': {'error': 'Environment not initialized'}
            }
        
        if env['done']:
            return {
                'observation': 'Episode already completed.',
                'reward': 0,
                'done': True,
                'info': {'message': 'Episode completed'}
            }
        
        env['step_count'] += 1
        
        # 检查是否超过最大步数
        if env['step_count'] >= env['max_steps']:
            env['done'] = True
            return {
                'observation': f'Maximum steps ({env["max_steps"]}) reached.',
                'reward': 0,
                'done': True,
                'info': {'reason': 'max_steps_reached'}
            }
        
        # 如果使用 ReactAgent
        if env.get('use_react_agent', False) and 'agent' in env:
            try:
                # ReactAgent 有自己的运行逻辑，我们需要检查它是否已经开始运行
                if not env.get('agent_started', False):
                    # 第一次调用时启动 ReactAgent
                    answer, scratchpad, json_log = env['agent'].run(env['query'])
                    env['agent_started'] = True
                    env['agent_result'] = answer
                    env['agent_scratchpad'] = scratchpad
                    env['done'] = True  # ReactAgent 运行完成后标记为完成
                    
                    return {
                        'observation': f'ReactAgent completed. Final answer: {answer}',
                        'reward': 1,
                        'done': True,
                        'info': {'step': env['step_count'], 'agent_type': 'react_agent', 'scratchpad': scratchpad}
                    }
                else:
                    # 如果 ReactAgent 已经运行完成
                    return {
                        'observation': f'ReactAgent already completed. Result: {env.get("agent_result", "No result")}',
                        'reward': 0,
                        'done': True,
                        'info': {'step': env['step_count'], 'agent_type': 'react_agent'}
                    }
            except Exception as e:
                return {
                    'observation': f'Error in ReactAgent: {str(e)}',
                    'reward': 0,
                    'done': False,
                    'info': {'error': str(e), 'step': env['step_count']}
                }
        
        # 解析动作
        try:
            observation, is_valid_action = self._execute_action(action)
            env['history'].append({'action': action, 'observation': observation})
            
            # 根据动作是否有效来设置奖励
            reward = 1 if is_valid_action else -1
            
            return {
                'observation': observation,
                'reward': reward,
                'done': False,
                'info': {'step': env['step_count'], 'agent_type': 'direct_tools', 'valid_action': is_valid_action}
            }
        except Exception as e:
            return {
                'observation': f'Error executing action: {str(e)}',
                'reward': 0,
                'done': False,
                'info': {'error': str(e), 'step': env['step_count']}
            }

    def _execute_action(self, action: str) -> tuple[str, bool]:
        """执行具体的动作，返回 (观察结果, 是否为有效动作)"""
        action = action.strip()
        
        # 解析动作格式
        if action.startswith('FlightSearch[') and action.endswith(']'):
            params = action[13:-1]  # 移除 'FlightSearch[' 和 ']'
            # 简单解析参数 (实际应该更robust)
            parts = [p.strip() for p in params.split(',')]
            if len(parts) >= 3:
                origin, destination, date = parts[0], parts[1], parts[2]
                result = self.flights.run(origin, destination, date)
                return str(result), True
            else:
                return "FlightSearch requires 3 parameters: origin, destination, date", False
        
        elif action.startswith('AccommodationSearch[') and action.endswith(']'):
            params = action[20:-1]
            city = params.strip()
            if city:
                result = self.accommodations.run(city)
                return str(result), True
            else:
                return "AccommodationSearch requires city parameter", False
        
        elif action.startswith('RestaurantSearch[') and action.endswith(']'):
            params = action[17:-1]
            city = params.strip()
            if city:
                result = self.restaurants.run(city)
                return str(result), True
            else:
                return "RestaurantSearch requires city parameter", False
        
        elif action.startswith('AttractionSearch[') and action.endswith(']'):
            params = action[17:-1]
            city = params.strip()
            if city:
                result = self.attractions.run(city)
                return str(result), True
            else:
                return "AttractionSearch requires city parameter", False
        
        elif action.startswith('DistanceMatrix[') and action.endswith(']'):
            params = action[15:-1]
            parts = [p.strip() for p in params.split(',')]
            if len(parts) >= 2:
                origin, destination = parts[0], parts[1]
                mode = parts[2] if len(parts) > 2 else 'driving'
                result = self.distance_matrix.run(origin, destination, mode)
                return str(result), True
            else:
                return "DistanceMatrix requires at least 2 parameters: origin, destination", False
        
        elif action.startswith('CitySearch[') and action.endswith(']'):
            params = action[11:-1]
            state = params.strip()
            if state:
                result = self.cities.run(state)
                return str(result), True
            else:
                return "CitySearch requires state parameter", False
        
        elif action.startswith('NotebookWrite[') and action.endswith(']'):
            params = action[14:-1]
            if params.strip():
                # 简化：直接存储文本
                result = self.notebook.write(params, "User note")
                return str(result), True
            else:
                return "NotebookWrite requires content parameter", False
        
        elif action.startswith('Planner[') and action.endswith(']'):  # 注释掉 planner 相关逻辑
            params = action[8:-1]
            result = self.planner.run("", params)
            return str(result), True
        
        else:
            return f"Unknown action format: {action}. Please use proper tool syntax like FlightSearch[origin, destination, date]", False

# 全局环境实例
travelplanner_env_server = TravelPlannerEnvironment(use_real_tools=True) 