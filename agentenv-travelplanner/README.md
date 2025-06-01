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
  "query": "Plan a 3-day trip to New York for 2 people with a budget of $2000",
  "use_react_agent": false
}
  ```
- **Response**:
  ```json
{
    "observation": "Environment reset successfully. Ready to plan: Plan a 3-day trip to New York for 2 people with a budget of $2000",
    "info": {
        "agent_type": "direct_tools"
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
  "action": "AccommodationSearch[New York]"
}
  ```
- **Response**:
  ```json
{
    "observation": "                    NAME  price        room type  ... maximum occupancy  review rate number      city\n0  Grand Hotel Manhattan    150     Private room  ...                 2                 4.5  New York\n1         Budget Inn NYC     80      Shared room  ...                 1                 3.8  New York\n2     Luxury Plaza Hotel    300  Entire home/apt  ...                 4                 4.8  New York\n3         Midtown Hostel     45      Shared room  ...                 1                 3.2  New York\n4    Central Park Suites    220     Private room  ...                 3                 4.2  New York\n5         Broadway Hotel    180     Private room  ...                 2                 4.1  New York\n6     Times Square Lodge    120      Shared room  ...                 2                 3.9  New York\n7   Manhattan Apartments    250  Entire home/apt  ...                 5                 4.4  New York\n\n[8 rows x 8 columns]",
    "reward": 1.0,
    "done": false,
    "info": {
        "step": 7,
        "agent_type": "direct_tools",
        "valid_action": true
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
