"""
Quick test for TravelPlanner Environment (without pytest)
"""

import sys
import traceback

try:
    from agentenv_travelplanner.environment import TravelPlannerEnvironment, TravelPlannerEnvServer
    print("✓ Successfully imported TravelPlanner environment classes")
except ImportError as e:
    print(f"✗ Failed to import environment classes: {e}")
    sys.exit(1)


def test_basic_functionality():
    """测试基本功能"""
    print("\n=== Testing Basic Functionality ===")
    
    try:
        # 测试环境初始化
        print("1. Testing environment initialization...")
        env = TravelPlannerEnvironment()
        assert env is not None
        assert len(env.available_tools) == 8
        print("   ✓ Environment initialized successfully")
        
        # 测试环境重置
        print("2. Testing environment reset...")
        result = env.reset(query_id=0)
        assert 'state' in result
        assert 'info' in result
        print("   ✓ Environment reset successful")
        
        # 测试动作解析
        print("3. Testing action parsing...")
        action = 'Action: FlightSearch with Action Input: {"departure_city": "New York", "destination_city": "Paris"}'
        tool_name, tool_input = env._parse_action(action)
        assert tool_name == "FlightSearch"
        assert tool_input["departure_city"] == "New York"
        print("   ✓ Action parsing works correctly")
        
        # 测试步骤执行
        print("4. Testing step execution...")
        state, reward, done, info = env.step(action)
        assert isinstance(state, str)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        print("   ✓ Step execution successful")
        
        print("✓ All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_server_functionality():
    """测试服务器功能"""
    print("\n=== Testing Server Functionality ===")
    
    try:
        # 测试服务器初始化
        print("1. Testing server initialization...")
        server = TravelPlannerEnvServer()
        assert server._max_id == 0
        print("   ✓ Server initialized successfully")
        
        # 测试环境创建
        print("2. Testing environment creation...")
        env_id = server.create()
        assert env_id == 0
        assert env_id in server.environments
        print("   ✓ Environment creation successful")
        
        # 测试环境重置
        print("3. Testing environment reset...")
        state, info = server.reset(env_id, query_id=0)
        assert isinstance(state, str)
        assert isinstance(info, dict)
        print("   ✓ Environment reset successful")
        
        # 测试环境步骤
        print("4. Testing environment step...")
        action = 'Action: AccommodationSearch with Action Input: {"city": "Tokyo"}'
        state, reward, done, info = server.step(env_id, action)
        assert isinstance(state, str)
        assert isinstance(reward, float)
        print("   ✓ Environment step successful")
        
        print("✓ All server functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Server functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_tool_execution():
    """测试工具执行"""
    print("\n=== Testing Tool Execution ===")
    
    try:
        env = TravelPlannerEnvironment()
        
        # 测试各种工具
        tools_to_test = [
            ("FlightSearch", {"departure_city": "NYC", "destination_city": "LAX", "date": "2024-06-01"}),
            ("AccommodationSearch", {"city": "Paris"}),
            ("RestaurantSearch", {"city": "Tokyo", "cuisine": "Japanese"}),
            ("AttractionSearch", {"city": "London"}),
            ("GoogleDistanceMatrix", {"origin": "A", "destination": "B"}),
            ("CitySearch", {"state": "California"}),
            ("NotebookWrite", {"content": "Test note"}),
            ("Planner", {"query": "Create plan"})
        ]
        
        for i, (tool_name, params) in enumerate(tools_to_test, 1):
            print(f"{i}. Testing {tool_name}...")
            result = env._execute_tool(tool_name, params)
            assert isinstance(result, str)
            assert len(result) > 0
            print(f"   ✓ {tool_name} executed successfully")
        
        print("✓ All tool execution tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Tool execution test failed: {e}")
        traceback.print_exc()
        return False


def test_integration():
    """集成测试"""
    print("\n=== Testing Integration ===")
    
    try:
        # 创建服务器
        server = TravelPlannerEnvServer()
        env_id = server.create()
        
        # 重置环境
        state, info = server.reset(env_id, 0)
        assert "Welcome to TravelPlanner" in state
        
        # 执行一系列动作
        actions = [
            'Action: FlightSearch with Action Input: {"departure_city": "Beijing", "destination_city": "Shanghai", "date": "2024-08-01"}',
            'Action: AccommodationSearch with Action Input: {"city": "Shanghai"}',
            'Action: NotebookWrite with Action Input: {"content": "Found good options for Shanghai trip"}',
            'Action: Planner with Action Input: {"query": "Create 2-day Shanghai travel plan"}'
        ]
        
        for i, action in enumerate(actions, 1):
            print(f"{i}. Executing action: {action[:50]}...")
            state, reward, done, info = server.step(env_id, action)
            assert reward >= 0  # 应该有正奖励或零奖励
            
            if done:
                print(f"   ✓ Task completed at step {i}")
                break
        
        print("✓ Integration test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("Running TravelPlanner Environment Quick Tests...")
    print("=" * 50)
    
    tests = [
        test_basic_functionality,
        test_server_functionality,
        test_tool_execution,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 