"""
Basic tests for TravelPlanner Environment
"""

import asyncio
import pytest
import httpx
from agentenv_travelplanner.environment import TravelPlannerEnvironment, TravelPlannerEnvServer


class TestTravelPlannerEnvironment:
    """测试 TravelPlanner 环境"""
    
    def test_environment_initialization(self):
        """测试环境初始化"""
        env = TravelPlannerEnvironment()
        assert env is not None
        assert len(env.available_tools) == 8
        assert env.step_count == 0
        assert env.max_steps == 30
    
    def test_environment_reset(self):
        """测试环境重置"""
        env = TravelPlannerEnvironment()
        result = env.reset(query_id=0)
        
        assert 'state' in result
        assert 'info' in result
        assert env.step_count == 0
        assert env.current_query is not None
        assert len(env.conversation_history) == 0
        assert len(env.notebook_content) == 0
    
    def test_action_parsing(self):
        """测试动作解析"""
        env = TravelPlannerEnvironment()
        env.reset()
        
        # 测试有效动作
        action = 'Action: FlightSearch with Action Input: {"departure_city": "New York", "destination_city": "Paris"}'
        tool_name, tool_input = env._parse_action(action)
        
        assert tool_name == "FlightSearch"
        assert tool_input["departure_city"] == "New York"
        assert tool_input["destination_city"] == "Paris"
        
        # 测试无效动作
        invalid_action = "Invalid action format"
        tool_name, tool_input = env._parse_action(invalid_action)
        assert tool_name is None
        assert tool_input is None
    
    def test_step_execution(self):
        """测试步骤执行"""
        env = TravelPlannerEnvironment()
        env.reset()
        
        action = 'Action: FlightSearch with Action Input: {"departure_city": "Tokyo", "destination_city": "Osaka", "date": "2024-07-15"}'
        state, reward, done, info = env.step(action)
        
        assert isinstance(state, str)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(info, dict)
        assert env.step_count == 1
        assert len(env.conversation_history) == 1
    
    def test_tool_execution(self):
        """测试工具执行"""
        env = TravelPlannerEnvironment()
        
        # 测试航班搜索
        result = env._execute_tool("FlightSearch", {"departure_city": "NYC", "destination_city": "LAX", "date": "2024-06-01"})
        assert "Found" in result
        assert "flights" in result
        
        # 测试住宿搜索
        result = env._execute_tool("AccommodationSearch", {"city": "Paris"})
        assert "Found" in result
        assert "accommodations" in result
        
        # 测试笔记写入
        result = env._execute_tool("NotebookWrite", {"content": "Test note"})
        assert "Successfully wrote to notebook" in result
        assert len(env.notebook_content) == 1
    
    def test_plan_generation(self):
        """测试计划生成"""
        env = TravelPlannerEnvironment()
        env.reset()
        
        # 添加一些笔记
        env._execute_tool("NotebookWrite", {"content": "Found good flights"})
        env._execute_tool("NotebookWrite", {"content": "Great hotels available"})
        
        # 生成计划
        result = env._execute_tool("Planner", {"query": "Create travel plan"})
        assert "Generated travel plan:" in result
        assert "Day 1:" in result
        assert "Budget Summary" in result


class TestTravelPlannerEnvServer:
    """测试 TravelPlanner 环境服务器"""
    
    def test_server_initialization(self):
        """测试服务器初始化"""
        server = TravelPlannerEnvServer()
        assert server._max_id == 0
        assert len(server.environments) == 0
        assert len(server.env_info) == 0
    
    def test_environment_creation(self):
        """测试环境创建"""
        server = TravelPlannerEnvServer()
        
        # 创建第一个环境
        env_id = server.create()
        assert env_id == 0
        assert env_id in server.environments
        assert env_id in server.env_info
        
        # 创建第二个环境
        env_id2 = server.create()
        assert env_id2 == 1
        assert len(server.environments) == 2
    
    def test_environment_reset(self):
        """测试环境重置"""
        server = TravelPlannerEnvServer()
        env_id = server.create()
        
        state, info = server.reset(env_id, query_id=0)
        assert isinstance(state, str)
        assert isinstance(info, dict)
        assert "query" in info
        assert "step_count" in info
    
    def test_environment_step(self):
        """测试环境步骤"""
        server = TravelPlannerEnvServer()
        env_id = server.create()
        server.reset(env_id, 0)
        
        action = 'Action: FlightSearch with Action Input: {"departure_city": "Berlin", "destination_city": "Munich", "date": "2024-08-01"}'
        state, reward, done, info = server.step(env_id, action)
        
        assert isinstance(state, str)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(info, dict)
    
    def test_environment_info(self):
        """测试获取环境信息"""
        server = TravelPlannerEnvServer()
        env_id = server.create()
        server.reset(env_id, 0)
        
        info = server.get_info(env_id)
        assert isinstance(info, dict)
        assert "step_count" in info
        assert "max_steps" in info
        assert "current_query" in info
    
    def test_invalid_environment_id(self):
        """测试无效环境ID"""
        server = TravelPlannerEnvServer()
        
        with pytest.raises(ValueError):
            server.reset(999, 0)
        
        with pytest.raises(ValueError):
            server.step(999, "test action")
        
        with pytest.raises(ValueError):
            server.get_info(999)


def test_integration():
    """集成测试"""
    # 创建服务器
    server = TravelPlannerEnvServer()
    
    # 创建环境
    env_id = server.create()
    
    # 重置环境
    state, info = server.reset(env_id, 0)
    assert "Welcome to TravelPlanner" in state
    
    # 执行一系列动作
    actions = [
        'Action: FlightSearch with Action Input: {"departure_city": "Sydney", "destination_city": "Melbourne", "date": "2024-09-01"}',
        'Action: AccommodationSearch with Action Input: {"city": "Melbourne"}',
        'Action: NotebookWrite with Action Input: {"content": "Found flights and hotels for Melbourne trip"}',
        'Action: Planner with Action Input: {"query": "Create 3-day Melbourne travel plan"}'
    ]
    
    total_reward = 0
    for action in actions:
        state, reward, done, info = server.step(env_id, action)
        total_reward += reward
        
        assert isinstance(state, str)
        assert reward >= 0  # 应该有正奖励
        
        if done:
            break
    
    # 验证最终状态
    final_info = server.get_info(env_id)
    assert final_info["step_count"] > 0
    assert len(final_info["conversation_history"]) > 0


if __name__ == "__main__":
    # 运行基础测试
    print("Running TravelPlanner Environment Tests...")
    
    test_env = TestTravelPlannerEnvironment()
    test_env.test_environment_initialization()
    test_env.test_environment_reset()
    test_env.test_action_parsing()
    test_env.test_step_execution()
    test_env.test_tool_execution()
    test_env.test_plan_generation()
    print("✓ Environment tests passed")
    
    test_server = TestTravelPlannerEnvServer()
    test_server.test_server_initialization()
    test_server.test_environment_creation()
    test_server.test_environment_reset()
    test_server.test_environment_step()
    test_server.test_environment_info()
    print("✓ Server tests passed")
    
    test_integration()
    print("✓ Integration tests passed")
    
    print("\nAll tests passed! 🎉") 