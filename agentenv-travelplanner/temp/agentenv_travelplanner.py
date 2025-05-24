import json
import os
import sys
import traceback
from typing import Any, Dict, Mapping
from pathlib import Path

# Add TravelPlanner to path
sys.path.append(os.path.join(os.path.dirname(__file__), "TravelPlanner"))
sys.path.append(os.path.join(os.path.dirname(__file__), "TravelPlanner", "agents"))
sys.path.append(os.path.join(os.path.dirname(__file__), "TravelPlanner", "tools"))

try:
    from agents.tool_agents import ReactAgent
    from evaluation.eval import eval_score
    from evaluation.commonsense_constraint import evaluation as commonsense_eval
    from evaluation.hard_constraint import evaluation as hard_eval
    from datasets import load_dataset
except ImportError as e:
    print(f"Warning: Could not import TravelPlanner modules: {e}")
    ReactAgent = None

# Import AgentGym base classes
from agentenv.controller import BaseEnvClient, BaseTask, ConversationMessage, StepOutput


class TravelPlannerEnvClient(BaseEnvClient):
    """
    TravelPlanner Environment Client for AgentGym
    
    This environment allows agents to:
    1. Use various travel tools (flights, hotels, restaurants, attractions)
    2. Generate comprehensive travel plans
    3. Have plans evaluated against constraints
    """
    
    conversation_start = (
        ConversationMessage(
            {
                "from": "human",
                "loss": None,
                "value": """You are a professional travel planner. Your task is to create comprehensive travel plans using available tools and information. 

Available tools:
1. FlightSearch[Departure City, Destination City, Date]: Search for flights
2. AccommodationSearch[City]: Find hotels and accommodations 
3. RestaurantSearch[City]: Discover dining options
4. AttractionSearch[City]: Find tourist attractions
5. GoogleDistanceMatrix[Origin, Destination, Mode]: Calculate travel distance and time
6. CitySearch[State]: Find cities in a state
7. NotebookWrite[Description]: Save information for planning
8. Planner[Query]: Generate final travel plan

Your response format should be:
Thought: [your reasoning]
Action: [tool_name] with Action Input: [parameters]

After collecting sufficient information, use the Planner tool to create a detailed travel plan including:
- Daily itinerary with specific times
- Transportation details (flight numbers, etc.)
- Accommodation bookings
- Restaurant reservations
- Attraction visits
- All plans must be realistic and follow constraints

Let's start planning!"""
            }
        ),
        ConversationMessage({"from": "gpt", "loss": False, "value": "I understand. I'm ready to help you create a comprehensive travel plan using the available tools. Please provide me with your travel requirements."}),
    )

    def __init__(self, data_len: int = 180, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_len = data_len
        self.current_id = 0
        self.agent = None
        self.current_query = None
        self.current_data = None
        self.step_count = 0
        self.max_steps = 30
        self.agent_scratchpad = ""
        self.final_plan = None
        self.reward = 0.0
        self.done = False
        
        # Load dataset
        try:
            self.dataset = load_dataset('osunlp/TravelPlanner', 'validation')['validation']
            self.data_len = len(self.dataset)
        except Exception as e:
            print(f"Warning: Could not load TravelPlanner dataset: {e}")
            self.dataset = None
            
        # Initialize agent
        if ReactAgent is not None:
            try:
                # Set required environment variables if not set
                if 'OPENAI_API_KEY' not in os.environ:
                    os.environ['OPENAI_API_KEY'] = 'dummy_key'
                if 'GOOGLE_API_KEY' not in os.environ:
                    os.environ['GOOGLE_API_KEY'] = 'dummy_key'
                
                # Initialize with minimal args
                class DummyArgs:
                    pass
                
                args = DummyArgs()
                self.agent = ReactAgent(
                    args=args,
                    mode='zero_shot',
                    tools=['FlightSearch', 'AccommodationSearch', 'RestaurantSearch', 
                          'AttractionSearch', 'GoogleDistanceMatrix', 'CitySearch', 
                          'NotebookWrite', 'Planner'],
                    max_steps=self.max_steps,
                    react_llm_name='gpt-3.5-turbo-1106',
                    planner_llm_name='gpt-3.5-turbo-1106'
                )
            except Exception as e:
                print(f"Warning: Could not initialize ReactAgent: {e}")
                self.agent = None

    def __len__(self) -> int:
        return self.data_len

    def observe(self) -> Dict[str, Any]:
        """Return current observation for the agent"""
        if self.current_query is None:
            return {"observation": "No travel query provided yet.", "step": self.step_count}
        
        if self.done:
            return {
                "observation": f"Task completed. Final plan generated: {self.final_plan is not None}",
                "step": self.step_count,
                "reward": self.reward
            }
        
        return {
            "observation": f"Travel Query: {self.current_query}\n"
                          f"Steps taken: {self.step_count}/{self.max_steps}\n"
                          f"Please use the available tools to gather information and create a travel plan.",
            "step": self.step_count
        }

    def step(self, action: str) -> StepOutput:
        """Execute action and return result"""
        self.step_count += 1
        
        if self.done or self.step_count > self.max_steps:
            return StepOutput(
                state="Task already completed or max steps reached.",
                reward=self.reward,
                done=True
            )
        
        try:
            # If we have an agent, try to use it
            if self.agent is not None:
                result = self._execute_with_agent(action)
            else:
                result = self._execute_mock_action(action)
                
            # Check if task is complete
            if "Planner" in action or self.step_count >= self.max_steps:
                self._finalize_plan(result)
                
            return StepOutput(
                state=result,
                reward=self.reward,
                done=self.done
            )
            
        except Exception as e:
            error_msg = f"Error executing action: {str(e)}\n{traceback.format_exc()}"
            return StepOutput(
                state=error_msg,
                reward=-1.0,
                done=False
            )

    def _execute_with_agent(self, action: str) -> str:
        """Execute action using the ReactAgent if available"""
        try:
            # Parse action format: "Action: ToolName with Action Input: {params}"
            if "Action:" in action and "with Action Input:" in action:
                action_part = action.split("Action:")[1].split("with Action Input:")[0].strip()
                input_part = action.split("with Action Input:")[1].strip()
                
                # Mock execution since we don't have full tool integration
                return f"Executed {action_part} with input {input_part}. Information gathered and saved to notebook."
            else:
                return f"Action format not recognized. Please use: Action: [tool_name] with Action Input: [parameters]"
                
        except Exception as e:
            return f"Error executing action with agent: {str(e)}"

    def _execute_mock_action(self, action: str) -> str:
        """Mock action execution when agent is not available"""
        action_lower = action.lower()
        
        if "flightsearch" in action_lower:
            return "Found several flight options. Flight F1234567 from New York to London on 2024-01-15, departure 08:30, arrival 20:45, price $650."
        elif "accommodationsearch" in action_lower:
            return "Found accommodations: Hotel London Plaza, 4-star, $200/night, excellent location near city center."
        elif "restaurantsearch" in action_lower:
            return "Found restaurants: The Local Bistro (British cuisine), Pasta Palace (Italian), Sushi Zen (Japanese)."
        elif "attractionsearch" in action_lower:
            return "Found attractions: British Museum, Tower of London, London Eye, Buckingham Palace."
        elif "googledistancematrix" in action_lower:
            return "Distance calculated: 15 km, 25 minutes by taxi, estimated cost $30."
        elif "citysearch" in action_lower:
            return "Cities found: London, Manchester, Liverpool, Birmingham."
        elif "notebookwrite" in action_lower:
            return "Information saved to notebook successfully."
        elif "planner" in action_lower:
            return self._generate_mock_plan()
        else:
            return f"Tool '{action}' executed. Information gathered."

    def _generate_mock_plan(self) -> str:
        """Generate a mock travel plan"""
        plan = """
Travel Plan Generated:

Day 1:
Current City: from New York to London
Transportation: Flight Number: F1234567, from New York to London, Departure Time: 08:30, Arrival Time: 20:45
Breakfast: -
Attraction: Tower of London, London
Lunch: The Local Bistro, London
Dinner: Pasta Palace, London
Accommodation: Hotel London Plaza, London

Day 2:
Current City: London
Transportation: -
Breakfast: Hotel breakfast, London
Attraction: British Museum, London; Buckingham Palace, London
Lunch: Sushi Zen, London
Dinner: Local pub, London
Accommodation: Hotel London Plaza, London

Day 3:
Current City: from London to New York
Transportation: Flight Number: F7654321, from London to New York, Departure Time: 14:30, Arrival Time: 18:15
Breakfast: Hotel breakfast, London
Attraction: London Eye, London
Lunch: Airport restaurant, London
Dinner: -
Accommodation: -
"""
        self.final_plan = plan
        return plan

    def _finalize_plan(self, plan_result: str):
        """Finalize the travel plan and calculate reward"""
        self.done = True
        self.final_plan = plan_result
        
        # Calculate reward based on plan quality
        if self.final_plan and len(self.final_plan) > 100:
            # Basic reward for generating a plan
            self.reward = 0.5
            
            # Additional reward for plan structure
            if "Day 1:" in self.final_plan and "Transportation:" in self.final_plan:
                self.reward += 0.3
                
            # Additional reward for including required elements
            required_elements = ["Accommodation:", "Restaurant", "Attraction:", "Flight"]
            for element in required_elements:
                if element in self.final_plan:
                    self.reward += 0.05
                    
            # Cap at 1.0
            self.reward = min(self.reward, 1.0)
        else:
            self.reward = 0.0

    def reset(self, id: int) -> Dict[str, Any]:
        """Reset environment with new travel query"""
        self.current_id = id
        self.step_count = 0
        self.done = False
        self.final_plan = None
        self.reward = 0.0
        self.agent_scratchpad = ""
        
        # Load query from dataset
        if self.dataset and id < len(self.dataset):
            self.current_data = self.dataset[id]
            self.current_query = self.current_data['query']
        else:
            # Fallback mock query
            self.current_query = f"Plan a 3-day trip to London for 2 people with a budget of $2000. We're interested in history and culture."
            self.current_data = {
                'query': self.current_query,
                'level': 'easy',
                'days': 3,
                'local_constraint': {}
            }
        
        return {
            "query": self.current_query,
            "id": id,
            "status": "Environment reset successfully"
        }


class TravelPlannerTask(BaseTask):
    """TravelPlanner Task for AgentGym"""
    env_client_cls = TravelPlannerEnvClient
    env_name = "TravelPlanner"

    def __init__(
        self,
        client_args: Mapping[str, Any],
        n_clients: int = 1,
        *args,
        **kwargs,
    ):
        super().__init__(client_args, n_clients, *args, **kwargs)

    def evaluate_plan(self, plan: str, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the generated travel plan against constraints
        
        Returns:
            Dict containing evaluation metrics
        """
        try:
            # Try to use actual TravelPlanner evaluation if available
            if commonsense_eval is not None and hard_eval is not None:
                # Parse plan into expected format
                plan_dict = self._parse_plan_to_dict(plan)
                
                # Evaluate constraints
                commonsense_info = commonsense_eval(query_data, plan_dict)
                hard_info = hard_eval(query_data, plan_dict) if commonsense_info else None
                
                return {
                    "commonsense_pass": all(commonsense_info.values()) if commonsense_info else False,
                    "hard_constraint_pass": all(hard_info.values()) if hard_info else False,
                    "commonsense_details": commonsense_info,
                    "hard_constraint_details": hard_info
                }
            else:
                # Fallback evaluation
                return self._mock_evaluation(plan, query_data)
                
        except Exception as e:
            print(f"Evaluation error: {e}")
            return self._mock_evaluation(plan, query_data)

    def _parse_plan_to_dict(self, plan: str) -> Dict[str, Any]:
        """Parse plan text into dictionary format expected by evaluators"""
        # This is a simplified parser - in practice would need more robust parsing
        plan_dict = {"days": []}
        
        days = plan.split("Day ")
        for day_text in days[1:]:  # Skip first empty split
            if day_text.strip():
                day_info = {
                    "transportation": "",
                    "breakfast": "",
                    "attraction": "",
                    "lunch": "",
                    "dinner": "",
                    "accommodation": ""
                }
                
                lines = day_text.split('\n')
                for line in lines:
                    if "Transportation:" in line:
                        day_info["transportation"] = line.split("Transportation:")[1].strip()
                    elif "Breakfast:" in line:
                        day_info["breakfast"] = line.split("Breakfast:")[1].strip()
                    elif "Attraction:" in line:
                        day_info["attraction"] = line.split("Attraction:")[1].strip()
                    elif "Lunch:" in line:
                        day_info["lunch"] = line.split("Lunch:")[1].strip()
                    elif "Dinner:" in line:
                        day_info["dinner"] = line.split("Dinner:")[1].strip()
                    elif "Accommodation:" in line:
                        day_info["accommodation"] = line.split("Accommodation:")[1].strip()
                
                plan_dict["days"].append(day_info)
        
        return plan_dict

    def _mock_evaluation(self, plan: str, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock evaluation when real evaluators are not available"""
        # Simple heuristic evaluation
        score = 0.0
        
        # Check if plan has basic structure
        if "Day 1:" in plan and "Day 2:" in plan:
            score += 0.3
            
        # Check for required components
        components = ["Transportation:", "Accommodation:", "Restaurant", "Attraction:"]
        for component in components:
            if component in plan:
                score += 0.15
                
        # Check for specific details
        if "Flight Number:" in plan:
            score += 0.1
        if "$" in plan or "price" in plan.lower():
            score += 0.1
            
        return {
            "commonsense_pass": score > 0.6,
            "hard_constraint_pass": score > 0.5,
            "overall_score": score,
            "evaluation_type": "mock"
        } 