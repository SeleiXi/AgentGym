## Installation

```bash
conda create -n agentenv-travelplanner python==3.12
conda activate agentenv-travelplanner
pip install -r requirements.txt
cd agentenv_travelplanner
python launch.py
```

## API Documentation

TravelPlanner Environment provides the following RESTful API endpoints:

### Basic Endpoints

#### 1. Connection Test
- **URL**: `/`
- **Method**: `GET`
- **Description**: Test server connection status
- **Response**: 
  ```json
  "This is TravelPlanner Environment for AgentGym"
  ```

#### 2. Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Check service health status
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "TravelPlanner Environment"
  }
  ```

### Environment Management Endpoints

#### 3. List All Environments
- **URL**: `/list_envs`
- **Method**: `GET`
- **Description**: Get a list of all active environment instance IDs
- **Response**: 
  ```json
  [0, 1, 2]
  ```

#### 4. Create New Environment
- **URL**: `/create`
- **Method**: `POST`
- **Description**: Create a new environment instance
- **Response**:
  ```json
  {
    "id": 0
  }
  ```

#### 5. Reset Environment
- **URL**: `/reset`
- **Method**: `POST`
- **Description**: Reset specified environment instance to initial state
- **Request Body**:
  ```json
  {
    "env_idx": 0,
    "query_id": 1
  }
  ```
- **Response**:
  ```json
  {
    "state": "Environment state description text",
    "info": {
      "query_id": 1,
      "query": "Plan a 5-day trip to Paris...",
      "level": "medium",
      "days": 5,
      "step_count": 0,
      "max_steps": 30,
      "available_tools": ["FlightSearch", "AccommodationSearch", ...]
    }
  }
  ```

### Environment Interaction Endpoints

#### 6. Execute Action
- **URL**: `/step`
- **Method**: `POST`
- **Description**: Execute an action in the specified environment
- **Request Body**:
  ```json
  {
    "env_idx": 0,
    "action": "Action: FlightSearch with Action Input: {\"departure_city\": \"New York\", \"destination_city\": \"Paris\", \"date\": \"2024-06-01\"}"
  }
  ```
- **Response**:
  ```json
  {
    "state": "Environment state after execution",
    "reward": 0.3,
    "done": false,
    "info": {
      "step_count": 1,
      "max_steps": 30,
      "tool_used": "FlightSearch",
      "tool_result": "Found 3 flights...",
      "conversation_history": [...],
      "notebook_content": [...]
    }
  }
  ```

#### 7. Get Environment Information
- **URL**: `/info`
- **Method**: `GET`
- **Parameters**: `env_idx` (query parameter)
- **Description**: Get detailed information of the specified environment
- **Example**: `/info?env_idx=0`
- **Response**:
  ```json
  {
    "info": {
      "step_count": 5,
      "max_steps": 30,
      "current_query": {
        "query": "Plan a 5-day trip to Paris",
        "level": "medium",
        "days": 5
      },
      "notebook_content": [...],
      "conversation_history": [...]
    }
  }
  ```

#### 8. Get Current Observation
- **URL**: `/observation`
- **Method**: `GET`
- **Parameters**: `env_idx` (query parameter)
- **Description**: Get current observation state of the specified environment
- **Example**: `/observation?env_idx=0`
- **Response**:
  ```json
  {
    "observation": "Step 5/30\nCurrent Query: Plan a 5-day trip to Paris...\n\nNotebook Contents:\n- Found great flight options...\n\nAvailable Tools: FlightSearch, AccommodationSearch, ..."
  }
  ```

### Available Tools

The environment provides the following tools for agents to use:

1. **FlightSearch** - Search flight information
2. **AccommodationSearch** - Search accommodation information
3. **RestaurantSearch** - Search restaurant information
4. **AttractionSearch** - Search attraction information
5. **GoogleDistanceMatrix** - Calculate distance and time
6. **CitySearch** - Search city information
7. **NotebookWrite** - Write to notebook
8. **Planner** - Generate travel plans

### Action Format

Agent actions should follow this format:

```
Action: [ToolName] with Action Input: [JSON parameters]
```

**Examples**:
```
Action: FlightSearch with Action Input: {"departure_city": "New York", "destination_city": "Paris", "date": "2024-06-01"}
Action: NotebookWrite with Action Input: {"content": "Found great flight options from New York to Paris"}
Action: Planner with Action Input: {"query": "Create a detailed 5-day travel plan for Paris"}
```

Default configuration:
- **Host**: `127.0.0.1`
- **Port**: `59399`
- **Log Level**: `info`
