"""
TravelPlanner Environment Implementation
"""

import os
import json
import random
import logging
from typing import Dict, Any, List, Tuple, Optional
from datasets import load_dataset
import yaml

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TravelPlannerEnvironment:
    """TravelPlanner 环境核心实现"""
    
    def __init__(self):
        self.dataset = None
        self.current_query = None
        self.conversation_history = []
        self.available_tools = [
            "FlightSearch", "AccommodationSearch", "RestaurantSearch", 
            "AttractionSearch", "GoogleDistanceMatrix", "CitySearch",
            "NotebookWrite", "Planner"
        ]
        self.notebook_content = []
        self.step_count = 0
        self.max_steps = 30
        self.load_dataset()
        
    def load_dataset(self):
        """加载 TravelPlanner 数据集"""
        try:
            # 尝试加载数据集，如果失败则使用模拟数据
            self.dataset = load_dataset("osunlp/TravelPlanner", split="validation")
            logger.info(f"Successfully loaded TravelPlanner dataset with {len(self.dataset)} samples")
        except Exception as e:
            logger.warning(f"Failed to load dataset: {e}, using mock data")
            self.dataset = self._create_mock_dataset()
    
    def _create_mock_dataset(self):
        """创建模拟数据集"""
        mock_data = []
        for i in range(10):
            mock_data.append({
                'query': f'Plan a {random.choice([3, 5, 7])}-day trip to {random.choice(["Paris", "Tokyo", "New York", "London"])} for {random.randint(1, 4)} people with a budget of ${random.randint(1000, 5000)}.',
                'level': random.choice(['easy', 'medium', 'hard']),
                'days': random.choice([3, 5, 7])
            })
        return mock_data
    
    def reset(self, query_id: int = 0) -> Dict[str, Any]:
        """重置环境"""
        self.step_count = 0
        self.conversation_history = []
        self.notebook_content = []
        
        # 获取查询
        if query_id < len(self.dataset):
            self.current_query = self.dataset[query_id]
        else:
            self.current_query = self.dataset[query_id % len(self.dataset)]
        
        initial_state = self._get_initial_state()
        
        return {
            'state': initial_state,
            'info': {
                'query_id': query_id,
                'query': self.current_query['query'],
                'level': self.current_query.get('level', 'medium'),
                'days': self.current_query.get('days', 5),
                'step_count': self.step_count,
                'max_steps': self.max_steps,
                'available_tools': self.available_tools
            }
        }
    
    def _get_initial_state(self) -> str:
        """获取初始状态描述"""
        return f"""Welcome to TravelPlanner! 

Travel Query: {self.current_query['query']}

You have access to the following tools:
{', '.join(self.available_tools)}

Your task is to gather information using the available tools and create a comprehensive travel plan. 

Please start by using tools to search for relevant information. Format your actions as:
Action: [ToolName] with Action Input: [JSON parameters]

Example:
Action: FlightSearch with Action Input: {{"departure_city": "New York", "destination_city": "Paris", "date": "2024-06-01"}}

You can also write information to your notebook:
Action: NotebookWrite with Action Input: {{"content": "Found great flight options..."}}

When ready to create the final plan:
Action: Planner with Action Input: {{"query": "Create a detailed travel plan based on gathered information"}}

What would you like to do first?"""
    
    def step(self, action: str) -> Tuple[str, float, bool, Dict[str, Any]]:
        """执行一步动作"""
        self.step_count += 1
        
        # 解析动作
        tool_name, tool_input = self._parse_action(action)
        
        if tool_name is None:
            return self._handle_invalid_action(action)
        
        # 执行工具
        result = self._execute_tool(tool_name, tool_input)
        
        # 更新对话历史
        self.conversation_history.append({
            'step': self.step_count,
            'action': action,
            'tool': tool_name,
            'input': tool_input,
            'result': result
        })
        
        # 计算奖励和是否完成
        reward = self._calculate_reward(tool_name, result)
        done = self._is_done(tool_name, result)
        
        # 构建新状态
        new_state = self._build_state(result, tool_name)
        
        info = {
            'step_count': self.step_count,
            'max_steps': self.max_steps,
            'tool_used': tool_name,
            'tool_result': result,
            'conversation_history': self.conversation_history,
            'notebook_content': self.notebook_content
        }
        
        return new_state, reward, done, info
    
    def _parse_action(self, action: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """解析动作字符串"""
        try:
            if "Action:" not in action:
                return None, None
            
            # 提取工具名和输入
            action_part = action.split("Action:")[1].strip()
            if " with Action Input:" in action_part:
                tool_name = action_part.split(" with Action Input:")[0].strip()
                input_part = action_part.split(" with Action Input:")[1].strip()
                
                # 解析 JSON 输入
                try:
                    tool_input = json.loads(input_part)
                except json.JSONDecodeError:
                    # 如果不是有效的 JSON，返回字符串
                    tool_input = {"query": input_part}
            else:
                tool_name = action_part.strip()
                tool_input = {}
            
            return tool_name, tool_input
            
        except Exception as e:
            logger.error(f"Failed to parse action: {e}")
            return None, None
    
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """执行工具调用"""
        if tool_name not in self.available_tools:
            return f"Error: Unknown tool '{tool_name}'. Available tools: {', '.join(self.available_tools)}"
        
        # 模拟工具执行结果
        if tool_name == "FlightSearch":
            return self._mock_flight_search(tool_input)
        elif tool_name == "AccommodationSearch":
            return self._mock_accommodation_search(tool_input)
        elif tool_name == "RestaurantSearch":
            return self._mock_restaurant_search(tool_input)
        elif tool_name == "AttractionSearch":
            return self._mock_attraction_search(tool_input)
        elif tool_name == "GoogleDistanceMatrix":
            return self._mock_distance_search(tool_input)
        elif tool_name == "CitySearch":
            return self._mock_city_search(tool_input)
        elif tool_name == "NotebookWrite":
            return self._handle_notebook_write(tool_input)
        elif tool_name == "Planner":
            return self._handle_planner(tool_input)
        else:
            return f"Tool '{tool_name}' is not implemented yet."
    
    def _mock_flight_search(self, params: Dict[str, Any]) -> str:
        """模拟航班搜索"""
        departure = params.get('departure_city', 'Unknown')
        destination = params.get('destination_city', 'Unknown')
        date = params.get('date', 'Unknown')
        
        flights = [
            f"Flight AA123: {departure} to {destination} on {date}, $450, 8:00AM-2:00PM",
            f"Flight UA456: {departure} to {destination} on {date}, $520, 10:30AM-4:30PM",
            f"Flight DL789: {departure} to {destination} on {date}, $380, 2:15PM-8:15PM"
        ]
        
        return f"Found {len(flights)} flights from {departure} to {destination} on {date}:\n" + "\n".join(flights)
    
    def _mock_accommodation_search(self, params: Dict[str, Any]) -> str:
        """模拟住宿搜索"""
        city = params.get('city', 'Unknown')
        
        hotels = [
            f"Grand Hotel {city}: 4-star, $150/night, downtown location",
            f"Budget Inn {city}: 3-star, $80/night, near airport",
            f"Luxury Resort {city}: 5-star, $300/night, city center"
        ]
        
        return f"Found {len(hotels)} accommodations in {city}:\n" + "\n".join(hotels)
    
    def _mock_restaurant_search(self, params: Dict[str, Any]) -> str:
        """模拟餐厅搜索"""
        city = params.get('city', 'Unknown')
        cuisine = params.get('cuisine', 'any')
        
        restaurants = [
            f"The Local Bistro: {cuisine} cuisine, $25-40 per person, 4.5/5 rating",
            f"Street Food Market: Various cuisines, $10-20 per person, 4.2/5 rating",
            f"Fine Dining Experience: {cuisine} cuisine, $60-100 per person, 4.8/5 rating"
        ]
        
        return f"Found {len(restaurants)} restaurants in {city} for {cuisine} cuisine:\n" + "\n".join(restaurants)
    
    def _mock_attraction_search(self, params: Dict[str, Any]) -> str:
        """模拟景点搜索"""
        city = params.get('city', 'Unknown')
        
        attractions = [
            f"{city} Museum: Historical museum, $15 entry, 9AM-5PM daily",
            f"{city} Central Park: Free outdoor space, perfect for walking",
            f"{city} Tower: Observation deck, $25 entry, great city views"
        ]
        
        return f"Found {len(attractions)} attractions in {city}:\n" + "\n".join(attractions)
    
    def _mock_distance_search(self, params: Dict[str, Any]) -> str:
        """模拟距离搜索"""
        origin = params.get('origin', 'Unknown')
        destination = params.get('destination', 'Unknown')
        
        distance = random.randint(5, 50)
        duration = random.randint(15, 120)
        
        return f"Distance from {origin} to {destination}: {distance} km, approximately {duration} minutes by car"
    
    def _mock_city_search(self, params: Dict[str, Any]) -> str:
        """模拟城市搜索"""
        state = params.get('state', 'Unknown')
        
        cities = [f"City A in {state}", f"City B in {state}", f"City C in {state}"]
        
        return f"Found {len(cities)} cities in {state}:\n" + "\n".join(cities)
    
    def _handle_notebook_write(self, params: Dict[str, Any]) -> str:
        """处理笔记写入"""
        content = params.get('content', '')
        self.notebook_content.append({
            'step': self.step_count,
            'content': content
        })
        
        return f"Successfully wrote to notebook: {content}"
    
    def _handle_planner(self, params: Dict[str, Any]) -> str:
        """处理计划生成"""
        # 使用提供的查询或默认查询
        if self.current_query is not None:
            query = params.get('query', self.current_query['query'])
        else:
            query = params.get('query', 'Create a travel plan')
        
        # 基于收集的信息生成计划
        plan = self._generate_travel_plan()
        
        return f"Generated travel plan:\n\n{plan}"
    
    def _generate_travel_plan(self) -> str:
        """生成旅行计划"""
        # 安全获取天数
        if self.current_query is not None and 'days' in self.current_query:
            days = self.current_query.get('days', 5)
        else:
            days = 5  # 默认5天
        
        plan_template = f"""# {days}-Day Travel Plan

## Day 1: Arrival
- Morning: Arrive via flight (based on searched flights)
- Afternoon: Check into hotel (based on accommodation search)
- Evening: Dinner at local restaurant

## Day 2-{days-1}: Exploration
- Visit attractions found during search
- Try recommended restaurants
- Explore local areas

## Day {days}: Departure
- Morning: Final shopping/sightseeing
- Afternoon: Check out and head to airport
- Evening: Departure flight

## Budget Summary
- Flights: ~$450 per person
- Accommodation: ~$150 per night
- Food: ~$50 per day per person
- Activities: ~$100 per day per person

## Notes from Research
"""
        
        # 添加笔记内容
        for note in self.notebook_content:
            plan_template += f"- {note['content']}\n"
        
        return plan_template
    
    def _calculate_reward(self, tool_name: str, result: str) -> float:
        """计算奖励"""
        reward = 0.1  # 基础奖励
        
        # 使用不同工具的奖励
        if tool_name in ["FlightSearch", "AccommodationSearch", "RestaurantSearch", "AttractionSearch"]:
            reward += 0.2
        elif tool_name == "NotebookWrite":
            reward += 0.1
        elif tool_name == "Planner":
            reward += 0.5  # 生成计划的高奖励
        
        # 错误惩罚
        if "Error:" in result:
            reward -= 0.3
        
        return max(0.0, reward)
    
    def _is_done(self, tool_name: str, result: str) -> bool:
        """判断是否完成"""
        # 如果使用了 Planner 工具且成功生成计划，则完成
        if tool_name == "Planner" and "Generated travel plan:" in result:
            return True
        
        # 如果达到最大步数
        if self.step_count >= self.max_steps:
            return True
        
        return False
    
    def _build_state(self, result: str, tool_name: str) -> str:
        """构建状态描述"""
        state = f"Step {self.step_count}/{self.max_steps}\n\n"
        state += f"Tool Result:\n{result}\n\n"
        
        if self.notebook_content:
            state += "Notebook Contents:\n"
            for note in self.notebook_content[-3:]:  # 显示最近3条笔记
                state += f"- {note['content']}\n"
            state += "\n"
        
        if tool_name != "Planner":
            state += "What would you like to do next? Available tools:\n"
            state += ", ".join(self.available_tools)
        
        return state
    
    def _handle_invalid_action(self, action: str) -> Tuple[str, float, bool, Dict[str, Any]]:
        """处理无效动作"""
        error_msg = f"Invalid action format: {action}\n\nPlease use the format:\nAction: [ToolName] with Action Input: [JSON parameters]"
        
        info = {
            'step_count': self.step_count,
            'max_steps': self.max_steps,
            'error': 'invalid_action_format'
        }
        
        return error_msg, -0.1, False, info


class TravelPlannerEnvServer:
    """TravelPlanner 环境服务器"""
    
    def __init__(self):
        self._max_id = 0
        self.environments = {}
        self.env_info = {}
    
    def create(self) -> int:
        """创建新的环境实例"""
        try:
            env_id = self._max_id
            self.environments[env_id] = TravelPlannerEnvironment()
            self.env_info[env_id] = {"created": True, "active": True}
            self._max_id += 1
            logger.info(f"Created new environment with ID: {env_id}")
            return env_id
        except Exception as e:
            logger.error(f"Failed to create environment: {e}")
            raise
    
    def reset(self, env_idx: int, query_id: int) -> Tuple[str, Dict[str, Any]]:
        """重置环境"""
        try:
            self._check_env_id(env_idx)
            reset_result = self.environments[env_idx].reset(query_id)
            logger.info(f"Reset environment {env_idx} with query_id {query_id}")
            return reset_result['state'], reset_result['info']
        except Exception as e:
            logger.error(f"Failed to reset environment {env_idx}: {e}")
            raise
    
    def step(self, env_idx: int, action: str) -> Tuple[str, float, bool, Dict[str, Any]]:
        """执行步骤"""
        try:
            self._check_env_id(env_idx)
            result = self.environments[env_idx].step(action)
            logger.info(f"Step in environment {env_idx}: {action[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Failed to step in environment {env_idx}: {e}")
            raise
    
    def get_info(self, env_idx: int) -> Dict[str, Any]:
        """获取环境信息"""
        try:
            self._check_env_id(env_idx)
            env = self.environments[env_idx]
            return {
                'step_count': env.step_count,
                'max_steps': env.max_steps,
                'current_query': env.current_query,
                'notebook_content': env.notebook_content,
                'conversation_history': env.conversation_history
            }
        except Exception as e:
            logger.error(f"Failed to get info for environment {env_idx}: {e}")
            raise
    
    def list_environments(self) -> List[int]:
        """列出所有环境"""
        return list(self.environments.keys())
    
    def _check_env_id(self, env_idx: int):
        """检查环境ID是否有效"""
        if env_idx not in self.environments:
            raise ValueError(f"Environment {env_idx} does not exist")
        if not self.env_info[env_idx]["active"]:
            raise ValueError(f"Environment {env_idx} is not active")


# 创建全局服务器实例
travelplanner_env_server = TravelPlannerEnvServer() 