"""
TravelPlanner Environment Utilities
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# 调试标志
debug_flg = os.getenv("DEBUG", "false").lower() == "true"

logger = logging.getLogger(__name__)


def safe_json_loads(json_str: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """安全地解析 JSON 字符串"""
    if default is None:
        default = {}
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {json_str}, error: {e}")
        return default


def format_action_result(tool_name: str, result: str, success: bool = True) -> str:
    """格式化动作执行结果"""
    status = "✓" if success else "✗"
    return f"[{status}] {tool_name}: {result}"


def extract_city_from_query(query: str) -> Optional[str]:
    """从查询中提取城市名称的简单方法"""
    # 简单的关键词匹配
    cities = ["Paris", "Tokyo", "New York", "London", "Rome", "Barcelona", "Sydney", "Dubai"]
    query_lower = query.lower()
    
    for city in cities:
        if city.lower() in query_lower:
            return city
    
    return None


def extract_days_from_query(query: str) -> int:
    """从查询中提取天数"""
    import re
    
    # 查找数字+天的模式
    patterns = [
        r'(\d+)[-\s]*day',
        r'(\d+)[-\s]*days',
        r'for\s+(\d+)\s+days?',
        r'(\d+)\s*天'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    
    return 5  # 默认5天


def extract_budget_from_query(query: str) -> Optional[int]:
    """从查询中提取预算"""
    import re
    
    # 查找金额模式
    patterns = [
        r'\$(\d+(?:,\d{3})*)',
        r'(\d+(?:,\d{3})*)\s*dollars?',
        r'budget\s+of\s+\$?(\d+(?:,\d{3})*)',
        r'(\d+(?:,\d{3})*)\s*元'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            try:
                # 移除逗号并转换为整数
                amount_str = match.group(1).replace(',', '')
                return int(amount_str)
            except ValueError:
                continue
    
    return None


def validate_tool_input(tool_name: str, tool_input: Dict[str, Any]) -> bool:
    """验证工具输入参数"""
    required_params = {
        "FlightSearch": ["departure_city", "destination_city"],
        "AccommodationSearch": ["city"],
        "RestaurantSearch": ["city"],
        "AttractionSearch": ["city"],
        "GoogleDistanceMatrix": ["origin", "destination"],
        "CitySearch": ["state"],
        "NotebookWrite": ["content"],
        "Planner": []
    }
    
    if tool_name not in required_params:
        return False
    
    required = required_params[tool_name]
    return all(param in tool_input for param in required)


def log_environment_action(env_id: int, step: int, action: str, result: str):
    """记录环境动作"""
    if debug_flg:
        logger.debug(f"Env {env_id} Step {step}: {action[:100]}... -> {result[:200]}...")


def get_mock_data_for_city(city: str) -> Dict[str, Any]:
    """获取城市的模拟数据"""
    mock_data = {
        "Paris": {
            "flights": ["CDG Airport", "Orly Airport"],
            "hotels": ["Hotel Ritz Paris", "Le Marais Hotel"],
            "restaurants": ["Le Jules Verne", "L'Ami Jean"],
            "attractions": ["Eiffel Tower", "Louvre Museum", "Arc de Triomphe"]
        },
        "Tokyo": {
            "flights": ["Narita Airport", "Haneda Airport"],
            "hotels": ["Park Hyatt Tokyo", "Hotel New Otani"],
            "restaurants": ["Sukiyabashi Jiro", "Narisawa"],
            "attractions": ["Tokyo Tower", "Senso-ji Temple", "Imperial Palace"]
        },
        "New York": {
            "flights": ["JFK Airport", "LaGuardia Airport"],
            "hotels": ["The Plaza", "The St. Regis"],
            "restaurants": ["Le Bernardin", "Eleven Madison Park"],
            "attractions": ["Statue of Liberty", "Central Park", "Times Square"]
        },
        "London": {
            "flights": ["Heathrow Airport", "Gatwick Airport"],
            "hotels": ["The Savoy", "Claridge's"],
            "restaurants": ["Gordon Ramsay", "Sketch"],
            "attractions": ["Big Ben", "Tower Bridge", "British Museum"]
        }
    }
    
    return mock_data.get(city, {
        "flights": [f"{city} Airport"],
        "hotels": [f"Grand Hotel {city}"],
        "restaurants": [f"The Local {city} Restaurant"],
        "attractions": [f"{city} Museum", f"{city} Park"]
    }) 