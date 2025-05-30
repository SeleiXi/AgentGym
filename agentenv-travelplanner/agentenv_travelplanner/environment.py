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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "TravelPlanner")))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TravelPlannerEnvironment:
    """TravelPlanner environment core implementation"""
    
    def __init__(self, use_react_agent=True, react_llm_name='gpt-3.5-turbo-1106', planner_llm_name='gpt-3.5-turbo-1106'):
        self.dataset = None
        self.current_query = None
        self.conversation_history = []
        self.step_count = 0
        self.max_steps = 30
        self.use_react_agent = use_react_agent
        self.react_llm_name = react_llm_name
        self.planner_llm_name = planner_llm_name
        
        # 如果使用 ReactAgent，初始化它
        if self.use_react_agent:
            self.react_agent = self._create_react_agent()
        else:
            self.react_agent = None
            
        self.load_dataset()
        
    def _create_react_agent(self):
        """创建 ReactAgent 实例"""
        try:
            from agents.tool_agents import ReactAgent
            
            tools_list = ["notebook", "flights", "attractions", "accommodations", 
                         "restaurants", "googleDistanceMatrix", "planner", "cities"]
            
            agent = ReactAgent(
                args=None,
                tools=tools_list,
                max_steps=self.max_steps,
                react_llm_name=self.react_llm_name,
                planner_llm_name=self.planner_llm_name
            )
            
            logger.info(f"Successfully created ReactAgent with {len(tools_list)} tools")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create ReactAgent: {e}")
            logger.warning("Falling back to mock mode")
            return None

    def load_dataset(self):
        """Load TravelPlanner dataset"""
        try:
            self.dataset = load_dataset("osunlp/TravelPlanner", split="validation")
            logger.info(f"Successfully loaded TravelPlanner dataset with {len(self.dataset)} samples")
        except Exception as e:
            logger.warning(f"Failed to load dataset: {e}, using mock data")
            self.dataset = self._create_mock_dataset()
    
    def _create_mock_dataset(self):
        """Create mock dataset"""
        mock_data = []
        for i in range(10):
            mock_data.append({
                'query': f'Plan a {random.choice([3, 5, 7])}-day trip to {random.choice(["Paris", "Tokyo", "New York", "London"])} for {random.randint(1, 4)} people with a budget of ${random.randint(1000, 5000)}.',
                'level': random.choice(['easy', 'medium', 'hard']),
                'days': random.choice([3, 5, 7])
            })
        return mock_data
    
    def reset(self, query_id: int = 0) -> Dict[str, Any]:
        """Reset environment"""
        self.step_count = 0
        self.conversation_history = []
        
        # Get query
        if query_id < len(self.dataset):
            self.current_query = self.dataset[query_id]
        else:
            self.current_query = self.dataset[query_id % len(self.dataset)]
        
        # 重置 ReactAgent
        if self.react_agent:
            self.react_agent.query = self.current_query['query']
            self.react_agent._ReactAgent__reset_agent()
        
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
                'using_react_agent': self.use_react_agent
            }
        }
    
    def _get_initial_state(self) -> str:
        """Get initial state description"""
        return f"""Welcome to TravelPlanner! 

Travel Query: {self.current_query['query']}

{'Using ReactAgent with real tools' if self.use_react_agent else 'Using mock tools'}

You can provide natural language instructions or thoughts, and the system will handle the tool calls automatically.

Example inputs:
- "I need to search for flights from New York to Los Angeles"
- "Find accommodations in Los Angeles"
- "Create a travel plan based on the information gathered"

What would you like to do first?"""
    
    def step(self, action: str) -> Tuple[str, float, bool, Dict[str, Any]]:
        """Execute one step"""
        self.step_count += 1
        
        if self.use_react_agent and self.react_agent:
            return self._step_with_react_agent(action)
        else:
            return self._step_with_mock(action)
    
    def _step_with_react_agent(self, user_input: str) -> Tuple[str, float, bool, Dict[str, Any]]:
        """使用 ReactAgent 执行步骤"""
        try:
            # 如果这是第一步，设置查询
            if self.step_count == 1:
                self.react_agent.query = self.current_query['query']
            
            # 获取当前状态
            previous_step_n = self.react_agent.step_n
            previous_scratchpad = self.react_agent.scratchpad
            
            # 执行一步
            self.react_agent.step()
            
            # 获取执行结果
            current_step_n = self.react_agent.step_n
            current_scratchpad = self.react_agent.scratchpad
            current_observation = self.react_agent.current_observation
            
            # 提取最新的 step 信息
            step_info = ""
            if self.react_agent.json_log:
                latest_log = self.react_agent.json_log[-1]
                step_info = f"Step {latest_log['step']}:\n"
                if latest_log['thought']:
                    step_info += f"Thought: {latest_log['thought']}\n"
                if latest_log['action']:
                    step_info += f"Action: {latest_log['action']}\n"
                if latest_log['observation']:
                    step_info += f"Observation: {latest_log['observation']}\n"
                if latest_log['state']:
                    step_info += f"State: {latest_log['state']}\n"
            
            # 记录对话历史
            self.conversation_history.append({
                'step': self.step_count,
                'user_input': user_input,
                'agent_step': current_step_n - 1,
                'step_info': step_info,
                'observation': current_observation
            })
            
            # 计算奖励
            reward = self._calculate_reward_from_agent()
            
            # 检查是否完成
            done = self.react_agent.is_finished() or self.react_agent.is_halted()
            
            # 构建状态描述
            new_state = self._build_state_from_agent(step_info)
            
            info = {
                'step_count': self.step_count,
                'agent_step': current_step_n - 1,
                'max_steps': self.max_steps,
                'agent_finished': self.react_agent.is_finished(),
                'agent_halted': self.react_agent.is_halted(),
                'conversation_history': self.conversation_history,
                'agent_json_log': self.react_agent.json_log,
                'agent_answer': self.react_agent.answer if done else None
            }
            
            return new_state, reward, done, info
            
        except Exception as e:
            logger.error(f"Error in ReactAgent step: {e}")
            error_msg = f"Error executing step: {str(e)}"
            info = {
                'step_count': self.step_count,
                'error': str(e)
            }
            return error_msg, -0.5, False, info
    
    def _step_with_mock(self, action: str) -> Tuple[str, float, bool, Dict[str, Any]]:
        """使用 mock 逻辑执行步骤"""
        # 简单的 mock 实现
        mock_response = f"Mock response for: {action[:50]}..."
        
        self.conversation_history.append({
            'step': self.step_count,
            'action': action,
            'response': mock_response
        })
        
        # 如果包含 "plan" 或 "finish"，则完成
        done = any(keyword in action.lower() for keyword in ['plan', 'finish', 'complete'])
        
        reward = 0.1 if not done else 0.5
        
        new_state = f"Step {self.step_count}: {mock_response}\n\nWhat would you like to do next?"
        
        info = {
            'step_count': self.step_count,
            'max_steps': self.max_steps,
            'conversation_history': self.conversation_history
        }
        
        return new_state, reward, done, info
    
    def _calculate_reward_from_agent(self) -> float:
        """基于 agent 状态计算奖励"""
        if not self.react_agent.json_log:
            return 0.0
        
        latest_log = self.react_agent.json_log[-1]
        state = latest_log.get('state', '')
        
        if 'Successful' in state:
            return 0.3
        elif 'Error' in state or 'Illegal' in state:
            return -0.1
        elif self.react_agent.is_finished():
            return 1.0
        else:
            return 0.1
    
    def _build_state_from_agent(self, step_info: str) -> str:
        """基于 agent 状态构建环境状态"""
        state = f"Step {self.step_count}/{self.max_steps}\n\n"
        state += step_info
        
        if self.react_agent.is_finished():
            state += f"\n\nAgent has completed the task!\nFinal Answer: {self.react_agent.answer}"
        elif self.react_agent.is_halted():
            state += "\n\nAgent has halted (max steps or token limit reached)."
        else:
            state += "\n\nAgent is continuing to work on the task..."
        
        return state


class TravelPlannerEnvServer:
    """TravelPlanner environment server"""
    
    def __init__(self, use_react_agent=True, react_llm_name='gpt-3.5-turbo-1106', planner_llm_name='gpt-3.5-turbo-1106'):
        self._max_id = 0
        self.environments = {}
        self.env_info = {}
        self.use_react_agent = use_react_agent
        self.react_llm_name = react_llm_name
        self.planner_llm_name = planner_llm_name
    
    def create(self, use_react_agent=None, react_llm_name=None, planner_llm_name=None) -> int:
        """Create new environment instance"""
        try:
            env_id = self._max_id
            
            # 使用传入的参数或默认参数
            use_agent = use_react_agent if use_react_agent is not None else self.use_react_agent
            react_model = react_llm_name if react_llm_name is not None else self.react_llm_name
            planner_model = planner_llm_name if planner_llm_name is not None else self.planner_llm_name
            
            self.environments[env_id] = TravelPlannerEnvironment(
                use_react_agent=use_agent,
                react_llm_name=react_model,
                planner_llm_name=planner_model
            )
            self.env_info[env_id] = {
                "created": True, 
                "active": True,
                "use_react_agent": use_agent,
                "react_llm_name": react_model,
                "planner_llm_name": planner_model
            }
            self._max_id += 1
            logger.info(f"Created new environment with ID: {env_id}, using ReactAgent: {use_agent}")
            return env_id
        except Exception as e:
            logger.error(f"Failed to create environment: {e}")
            raise
    
    def reset(self, env_idx: int, query_id: int) -> Tuple[str, Dict[str, Any]]:
        """Reset environment"""
        try:
            self._check_env_id(env_idx)
            reset_result = self.environments[env_idx].reset(query_id)
            logger.info(f"Reset environment {env_idx} with query_id {query_id}")
            return reset_result['state'], reset_result['info']
        except Exception as e:
            logger.error(f"Failed to reset environment {env_idx}: {e}")
            raise
    
    def step(self, env_idx: int, action: str) -> Tuple[str, float, bool, Dict[str, Any]]:
        """Execute step"""
        try:
            self._check_env_id(env_idx)
            result = self.environments[env_idx].step(action)
            logger.info(f"Step in environment {env_idx}: {action[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Failed to step in environment {env_idx}: {e}")
            raise
    
    def get_info(self, env_idx: int) -> Dict[str, Any]:
        """Get environment information"""
        try:
            self._check_env_id(env_idx)
            env = self.environments[env_idx]
            info = {
                'step_count': env.step_count,
                'max_steps': env.max_steps,
                'current_query': env.current_query,
                'conversation_history': env.conversation_history,
                'using_react_agent': env.use_react_agent
            }
            
            # 如果使用 ReactAgent，添加额外信息
            if env.react_agent:
                info.update({
                    'agent_step_n': env.react_agent.step_n,
                    'agent_finished': env.react_agent.is_finished(),
                    'agent_halted': env.react_agent.is_halted(),
                    'agent_answer': env.react_agent.answer,
                    'agent_json_log': env.react_agent.json_log
                })
            
            return info
        except Exception as e:
            logger.error(f"Failed to get info for environment {env_idx}: {e}")
            raise
    
    def list_environments(self) -> List[int]:
        """List all environments"""
        return list(self.environments.keys())
    
    def _check_env_id(self, env_idx: int):
        """Check if environment ID is valid"""
        if env_idx not in self.environments:
            raise ValueError(f"Environment {env_idx} does not exist")
        if not self.env_info[env_idx]["active"]:
            raise ValueError(f"Environment {env_idx} is not active")


# Create global server instance
travelplanner_env_server = TravelPlannerEnvServer() 


# 使用示例
if __name__ == "__main__":
    """
    使用 TravelPlanner ReactAgent 的示例
    """
    import os
    
    # 确保环境变量已设置
    required_env_vars = ['OPENAI_API_KEY']
    for var in required_env_vars:
        if var not in os.environ:
            print(f"Warning: {var} not set in environment variables")
    
    # 创建使用 ReactAgent 的环境服务器
    server = TravelPlannerEnvServer(
        use_react_agent=True,  # 使用 ReactAgent
        react_llm_name='gpt-3.5-turbo-1106',
        planner_llm_name='gpt-3.5-turbo-1106'
    )
    
    try:
        # 创建环境实例
        env_id = server.create()
        print(f"Created environment {env_id}")
        
        # 重置环境
        state, info = server.reset(env_id, query_id=0)
        print("Initial state:", state[:200] + "...")
        print("Environment info:", info)
        
        # 示例：让 ReactAgent 自动执行
        # 由于 ReactAgent 的 step() 是自主的，我们只需要触发它
        for i in range(5):  # 最多执行5步
            print(f"\n--- Environment Step {i+1} ---")
            
            # 简单的触发输入
            user_input = f"Continue step {i+1}"
            state, reward, done, info = server.step(env_id, user_input)
            
            print(f"Reward: {reward}")
            print(f"Done: {done}")
            print(f"Agent step: {info.get('agent_step', 'N/A')}")
            print(f"New state: {state[:300] + '...' if len(state) > 300 else state}")
            
            if done:
                print("Environment finished!")
                if info.get('agent_answer'):
                    print(f"Final Answer: {info['agent_answer']}")
                break
        
        # 获取最终信息
        final_info = server.get_info(env_id)
        print("\nFinal environment info:")
        print(f"Environment steps: {final_info['step_count']}")
        print(f"Agent steps: {final_info.get('agent_step_n', 'N/A')}")
        print(f"Agent finished: {final_info.get('agent_finished', False)}")
        
    except Exception as e:
        print(f"Error running example: {e}")
        print("This might be due to missing dependencies or API keys")
        print("To use mock mode instead, set use_react_agent=False") 