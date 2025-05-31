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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TravelPlannerEnvironment:
    """TravelPlanner environment core implementation"""
    
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
        """Load TravelPlanner dataset"""
        try:
            # Try to load dataset, use mock data if failed
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
        self.notebook_content = []
        
        # Get query
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
        """Get initial state description"""
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
        """Execute one step action"""
        self.step_count += 1
        
        
        # Parse action
        tool_name, tool_input = self._parse_action(action)
        
        if tool_name is None:
            return self._handle_invalid_action(action)
        
        # Execute tool
        result = self._execute_tool(tool_name, tool_input)
        
        # Update conversation history
        self.conversation_history.append({
            'step': self.step_count,
            'action': action,
            'tool': tool_name,
            'input': tool_input,
            'result': result
        })
        
        # Calculate reward and completion status
        reward = self._calculate_reward(tool_name, result)
        done = self._is_done(tool_name, result)
        
        # Build new state
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
        """Parse action string"""
        try:
            if "Action:" not in action:
                return None, None
            
            # Extract tool name and input
            action_part = action.split("Action:")[1].strip()
            if " with Action Input:" in action_part:
                tool_name = action_part.split(" with Action Input:")[0].strip()
                input_part = action_part.split(" with Action Input:")[1].strip()
                
                # Parse JSON input
                try:
                    tool_input = json.loads(input_part)
                except json.JSONDecodeError:
                    # If not valid JSON, return as string
                    tool_input = {"query": input_part}
            else:
                tool_name = action_part.strip()
                tool_input = {}
            
            return tool_name, tool_input
            
        except Exception as e:
            logger.error(f"Failed to parse action: {e}")
            return None, None
    
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute tool call"""
        if tool_name not in self.available_tools:
            return f"Error: Unknown tool '{tool_name}'. Available tools: {', '.join(self.available_tools)}"
        
        # Mock tool execution results
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
        """Mock flight search"""
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
        """Mock accommodation search"""
        city = params.get('city', 'Unknown')
        
        hotels = [
            f"Grand Hotel {city}: 4-star, $150/night, downtown location",
            f"Budget Inn {city}: 3-star, $80/night, near airport",
            f"Luxury Resort {city}: 5-star, $300/night, city center"
        ]
        
        return f"Found {len(hotels)} accommodations in {city}:\n" + "\n".join(hotels)
    
    def _mock_restaurant_search(self, params: Dict[str, Any]) -> str:
        """Mock restaurant search"""
        city = params.get('city', 'Unknown')
        cuisine = params.get('cuisine', 'any')
        
        restaurants = [
            f"The Local Bistro: {cuisine} cuisine, $25-40 per person, 4.5/5 rating",
            f"Street Food Market: Various cuisines, $10-20 per person, 4.2/5 rating",
            f"Fine Dining Experience: {cuisine} cuisine, $60-100 per person, 4.8/5 rating"
        ]
        
        return f"Found {len(restaurants)} restaurants in {city} for {cuisine} cuisine:\n" + "\n".join(restaurants)
    
    def _mock_attraction_search(self, params: Dict[str, Any]) -> str:
        """Mock attraction search"""
        city = params.get('city', 'Unknown')
        
        attractions = [
            f"{city} Museum: Historical museum, $15 entry, 9AM-5PM daily",
            f"{city} Central Park: Free outdoor space, perfect for walking",
            f"{city} Tower: Observation deck, $25 entry, great city views"
        ]
        
        return f"Found {len(attractions)} attractions in {city}:\n" + "\n".join(attractions)
    
    def _mock_distance_search(self, params: Dict[str, Any]) -> str:
        """Mock distance search"""
        origin = params.get('origin', 'Unknown')
        destination = params.get('destination', 'Unknown')
        
        distance = random.randint(5, 50)
        duration = random.randint(15, 120)
        
        return f"Distance from {origin} to {destination}: {distance} km, approximately {duration} minutes by car"
    
    def _mock_city_search(self, params: Dict[str, Any]) -> str:
        """Mock city search"""
        state = params.get('state', 'Unknown')
        
        cities = [f"City A in {state}", f"City B in {state}", f"City C in {state}"]
        
        return f"Found {len(cities)} cities in {state}:\n" + "\n".join(cities)
    
    def _handle_notebook_write(self, params: Dict[str, Any]) -> str:
        """Handle notebook writing"""
        content = params.get('content', '')
        self.notebook_content.append({
            'step': self.step_count,
            'content': content
        })
        
        return f"Successfully wrote to notebook: {content}"
    
    def _handle_planner(self, params: Dict[str, Any]) -> str:
        """Handle plan generation"""
        # Use provided query or default query
        if self.current_query is not None:
            query = params.get('query', self.current_query['query'])
        else:
            query = params.get('query', 'Create a travel plan')
        
        # Generate plan based on collected information
        plan = self._generate_travel_plan()
        
        return f"Generated travel plan:\n\n{plan}"
    
    def _generate_travel_plan(self) -> str:
        """Generate travel plan"""
        # Safe get days
        if self.current_query is not None and 'days' in self.current_query:
            days = self.current_query.get('days', 5)
        else:
            days = 5  # Default 5 days
        
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
        
        # Add note contents
        for note in self.notebook_content:
            plan_template += f"- {note['content']}\n"
        
        return plan_template
    
    def _calculate_reward(self, tool_name: str, result: str) -> float:
        """Calculate reward"""
        reward = 0.1  # Base reward
        
        # Use different tool rewards
        if tool_name in ["FlightSearch", "AccommodationSearch", "RestaurantSearch", "AttractionSearch"]:
            reward += 0.2
        elif tool_name == "NotebookWrite":
            reward += 0.1
        elif tool_name == "Planner":
            reward += 0.5  # High reward for generating plan
        
        # Error penalty
        if "Error:" in result:
            reward -= 0.3
        
        return max(0.0, reward)
    
    def _is_done(self, tool_name: str, result: str) -> bool:
        """Determine if done"""
        # If Planner tool used and plan generated successfully, then done
        if tool_name == "Planner" and "Generated travel plan:" in result:
            return True
        
        # If reach max steps
        if self.step_count >= self.max_steps:
            return True
        
        return False
    
    def _build_state(self, result: str, tool_name: str) -> str:
        """Build state description"""
        state = f"Step {self.step_count}/{self.max_steps}\n\n"
        state += f"Tool Result:\n{result}\n\n"
        
        if self.notebook_content:
            state += "Notebook Contents:\n"
            for note in self.notebook_content[-3:]:  # Show recent 3 notes
                state += f"- {note['content']}\n"
            state += "\n"
        
        if tool_name != "Planner":
            state += "What would you like to do next? Available tools:\n"
            state += ", ".join(self.available_tools)
        
        return state
    
    def _handle_invalid_action(self, action: str) -> Tuple[str, float, bool, Dict[str, Any]]:
        """Handle invalid action"""
        error_msg = f"Invalid action format: {action}\n\nPlease use the format:\nAction: [ToolName] with Action Input: [JSON parameters]"
        
        info = {
            'step_count': self.step_count,
            'max_steps': self.max_steps,
            'error': 'invalid_action_format'
        }
        
        return error_msg, -0.1, False, info


class TravelPlannerEnvServer:
    """TravelPlanner environment server"""
    
    def __init__(self):
        self._max_id = 0
        self.environments = {}
        self.env_info = {}
    
    def create(self) -> int:
        """Create new environment instance"""
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