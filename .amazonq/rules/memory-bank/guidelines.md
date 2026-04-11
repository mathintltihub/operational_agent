# Development Guidelines

## Code Quality Standards

### Documentation Style
- **Module Docstrings**: Every Python module starts with a triple-quoted docstring describing its purpose
  ```python
  """
  Operations Agent - FastAPI Backend
  IT Operations Ticket Triage System - Chatbot Edition
  """
  ```
- **Function Docstrings**: All public functions include docstrings explaining their purpose
  ```python
  def analyze_ticket(request: TicketRequest):
      """
      Analyze a support ticket and return classification results.
      """
  ```
- **Inline Comments**: Used sparingly for complex logic, with clear explanations
  ```python
  # --- Identity skill: handle greetings / who-are-you locally ---
  ```

### Naming Conventions
- **Python Variables**: snake_case for variables, functions, and module names
  - `conversation_id`, `user_message`, `issue_type`, `confidence_score`
- **Python Classes**: PascalCase for class names
  - `LocalTicketAnalyzer`, `ChatMessage`, `TicketResponse`
- **Python Constants**: UPPERCASE_WITH_UNDERSCORES for constants
  - `SAMPLE_TICKETS`, `SKILL_TRIGGERS`, `RESPONSES`, `API_BASE`
- **JavaScript Variables**: camelCase for variables and functions
  - `conversationId`, `isProcessing`, `chatMessages`, `sendMessage`
- **JavaScript Constants**: UPPERCASE_WITH_UNDERSCORES for API configuration
  - `API_BASE`
- **Private Methods**: Leading underscore for internal Python methods
  - `_detect_issue_type()`, `_calculate_confidence()`, `_get_team()`

### File Organization
- **Imports Grouped**: Standard library → Third-party → Local imports
  ```python
  import os
  import sys
  from pathlib import Path
  from datetime import datetime
  
  from dotenv import load_dotenv
  from fastapi import FastAPI, HTTPException
  
  from backend.schemas import TicketRequest
  from backend.services.analyzer import analyzer
  ```
- **Logical Sections**: Code organized with clear section separators
  ```python
  # ---------------------------------------------------------------------------
  # Trigger maps — each key is a skill name, value is list of trigger phrases
  # ---------------------------------------------------------------------------
  ```

### Type Hints
- **Comprehensive Type Annotations**: All function parameters and return types annotated
  ```python
  def analyze(self, title: str, description: str) -> dict:
  def detect_skill(message: str) -> str:
  def get_logs(limit: int = 100):
  ```
- **Pydantic Models**: Used for all API request/response schemas with Field validators
  ```python
  class ChatRequest(BaseModel):
      message: str = Field(..., min_length=1, max_length=2000, description="User message")
      conversation_id: Optional[str] = Field(None, description="Conversation ID for history")
  ```

## Architectural Patterns

### Service Layer Pattern
- **Singleton Services**: Core services instantiated as module-level singletons
  ```python
  # Singleton instance
  analyzer = LocalTicketAnalyzer()
  ```
- **Service Separation**: Each service has a dedicated file with single responsibility
  - `analyzer.py` - Ticket analysis logic
  - `logger.py` - Logging operations
  - `identity_skill.py` - Conversational responses
  - `sample_data.py` - Test data

### Schema-First Design
- **Pydantic Validation**: All API inputs/outputs validated through Pydantic models
- **Field Constraints**: Explicit validation rules on fields
  ```python
  title: str = Field(..., min_length=1, max_length=500, description="Ticket title")
  confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
  ```
- **Automatic Serialization**: Models handle JSON conversion automatically

### Keyword-Based Classification
- **Dictionary Mapping**: Issue types, priorities, and teams mapped via dictionaries
  ```python
  mapping = {
      "database": "Database Team",
      "network": "Network Team",
      "server": "Server Team"
  }
  ```
- **Keyword Lists**: Classification based on keyword presence in text
  ```python
  if any(kw in text for kw in ["database", "db ", "postgres", "mysql"]):
      return "database"
  ```

### Conversational Skill Routing
- **Trigger-Based Routing**: Messages routed to skills based on trigger phrase matching
  ```python
  def detect_skill(message: str) -> str:
      msg = message.lower().strip()
      for skill, triggers in SKILL_TRIGGERS.items():
          if any(trigger in msg for trigger in triggers):
              return skill
      return None  # Route to ticket analyzer
  ```
- **Pre-defined Responses**: Static responses for common conversational patterns
- **Fallback Logic**: Unknown messages default to ticket analysis

### Error Handling
- **HTTPException**: FastAPI exceptions with status codes and detail messages
  ```python
  if not request.title.strip():
      raise HTTPException(status_code=400, detail="Title cannot be empty")
  ```
- **Try-Except Blocks**: Graceful error handling with user-friendly messages
  ```python
  try:
      result = analyzer.analyze(title=title, description=description)
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
  ```

## API Design Patterns

### RESTful Endpoints
- **Resource-Based URLs**: Clear, hierarchical endpoint structure
  - `GET /health` - Health check
  - `POST /analyze-ticket` - Ticket analysis
  - `GET /sample-tickets` - Sample data
  - `GET /logs` - List logs
  - `GET /logs/{ticket_id}` - Specific log
  - `DELETE /logs` - Clear logs
  - `POST /chat` - Chat interface
  - `GET /conversation/{conversation_id}` - Conversation history
  - `DELETE /conversation/{conversation_id}` - Delete conversation

### Response Models
- **Consistent Structure**: All endpoints return typed response models
  ```python
  @app.get("/health", response_model=HealthResponse)
  @app.post("/analyze-ticket", response_model=TicketResponse)
  @app.post("/chat", response_model=ChatResponse)
  ```
- **Nested Models**: Complex responses use nested Pydantic models
  ```python
  class ChatResponse(BaseModel):
      conversation_id: str
      message: ChatMessage
      analysis: Optional[TicketResponse] = None
  ```

### CORS Configuration
- **Permissive Development CORS**: Allow all origins for local development
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

## Frontend Patterns

### State Management
- **Module-Level State**: Global state variables at top of file
  ```javascript
  let conversationId = null;
  let isProcessing = false;
  ```
- **DOM Element Caching**: Cache DOM elements in object for reuse
  ```javascript
  const elements = {
      chatMessages: document.getElementById('chat-messages'),
      messageInput: document.getElementById('message-input'),
      sendBtn: document.getElementById('send-btn')
  };
  ```

### Event Handling
- **Centralized Setup**: All event listeners configured in single function
  ```javascript
  function setupEventListeners() {
      elements.sendBtn.addEventListener('click', sendMessage);
      elements.clearChatBtn.addEventListener('click', clearChat);
      // ... more listeners
  }
  ```
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for new line
  ```javascript
  elements.messageInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
      }
  });
  ```

### Async API Calls
- **Fetch API**: Modern async/await pattern for HTTP requests
  ```javascript
  async function sendMessage() {
      const response = await fetch(`${API_BASE}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: message, conversation_id: conversationId })
      });
      const result = await response.json();
  }
  ```
- **Error Handling**: Try-catch blocks with user-friendly error messages
  ```javascript
  try {
      const response = await fetch(...);
      if (!response.ok) throw new Error(errorData.detail || 'Failed to send message');
  } catch (error) {
      addMessage('assistant', `Error: ${error.message}. Please try again.`);
  }
  ```

### UI Updates
- **Dynamic HTML Generation**: Template literals for dynamic content
  ```javascript
  messageDiv.innerHTML = `
      <div class="message-avatar">${avatarSvg}</div>
      <div class="message-content">
          <div class="message-bubble">${formattedContent}</div>
          <div class="message-time">${formatTime(new Date())}</div>
      </div>
  `;
  ```
- **Progressive Enhancement**: Show loading states during async operations
  ```javascript
  isProcessing = true;
  elements.sendBtn.disabled = true;
  const typingIndicator = showTypingIndicator();
  // ... perform operation
  typingIndicator.remove();
  isProcessing = false;
  elements.sendBtn.disabled = false;
  ```

### Content Formatting
- **Markdown-Like Parsing**: Convert simple markdown to HTML
  ```javascript
  function formatMessageContent(content) {
      return content
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/\n\n/g, '<br><br>')
          .replace(/\n/g, '<br>');
  }
  ```
- **Emoji Support**: Preserve and wrap emojis in spans for styling

## Testing Patterns

### Test Structure
- **Descriptive Test Names**: Clear function names describing what's tested
  ```python
  def test_health():
  def test_sample_tickets():
  def test_analyze_ticket():
  ```
- **Test Cases with Expected Results**: Each test includes expected outcomes
  ```python
  test_cases = [
      {
          "title": "Cannot connect to production database",
          "description": "...",
          "expected_type": "database"
      }
  ]
  ```

### Assertion Pattern
- **Status Code Validation**: Always check HTTP status codes
  ```python
  assert response.status_code == 200
  ```
- **Result Validation**: Compare actual vs expected results
  ```python
  if test['expected_type'] == result['issue_type']:
      print(f"    MATCH ✓")
  ```

### Test Output
- **Structured Output**: Clear test progress and results
  ```python
  print("\n[TEST] Health Check")
  print(f"  Status: {data['status']}")
  print("  PASSED")
  ```
- **Summary Report**: Final pass/fail count
  ```python
  print(f"Results: {sum(results)}/{len(results)} tests passed")
  ```

## Configuration Management

### Environment Variables
- **dotenv Pattern**: Load environment variables from .env file
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```
- **Optional API Keys**: Graceful fallback when API keys not present
- **Example Files**: Provide .env.example as template

### Path Management
- **Pathlib Usage**: Use Path objects for cross-platform compatibility
  ```python
  from pathlib import Path
  project_root = Path(__file__).parent.parent
  ```
- **Dynamic Path Resolution**: Resolve paths relative to project root

## Data Persistence

### JSON File Storage
- **Simple Persistence**: Use JSON files for local data storage
- **Human-Readable**: JSON format allows manual inspection
- **No Database Required**: Eliminates setup complexity for MVP

### In-Memory Storage
- **Conversation History**: Store active conversations in memory
  ```python
  conversations = {}  # In-memory conversation store
  ```
- **Session Management**: Generate unique IDs for sessions
  ```python
  conversation_id = f"conv-{uuid.uuid4().hex[:8]}"
  ```

## Code Idioms

### Dictionary Get with Default
```python
return mapping.get(issue_type, "Manual Review")
priority_emoji.get(priority, '⚪')
```

### List Comprehension for Filtering
```python
if any(kw in text for kw in ["database", "db ", "postgres"]):
```

### String Formatting
- **f-strings**: Preferred for string interpolation
  ```python
  f"Analysis failed: {str(e)}"
  f"ticket-{uuid.uuid4().hex[:8]}"
  ```
- **Template Literals (JS)**: For multi-line HTML generation
  ```javascript
  `<div class="message ${role}-message">...</div>`
  ```

### Ternary Expressions
```python
network_url = f"http://{network_ip}:8000" if network_ip != "Unavailable" else "Unavailable"
```

### Method Chaining
```python
request.title.strip()
message.lower().strip()
```

## Common Annotations

### Pydantic Field Annotations
```python
Field(..., min_length=1, max_length=500, description="Ticket title")
Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
Field(default_factory=lambda: datetime.utcnow().isoformat())
```

### FastAPI Route Decorators
```python
@app.get("/health", response_model=HealthResponse)
@app.post("/analyze-ticket", response_model=TicketResponse)
@app.delete("/logs")
```

### Type Hints
```python
from typing import List, Optional
async def get_logs(limit: int = 100):
def analyze(self, title: str, description: str) -> dict:
```

## Best Practices Observed

### Security
- **Input Validation**: All user inputs validated through Pydantic
- **Strip Whitespace**: Always strip user input before processing
- **Error Message Safety**: Don't expose internal details in error messages

### Performance
- **Singleton Pattern**: Reuse service instances
- **DOM Caching**: Cache frequently accessed DOM elements
- **Minimal API Calls**: Batch operations where possible

### Maintainability
- **Single Responsibility**: Each module/function has one clear purpose
- **DRY Principle**: Reusable functions for common operations
- **Clear Separation**: Frontend, backend, services, schemas all separated
- **Configuration Externalization**: API keys and settings in environment variables

### User Experience
- **Loading States**: Show typing indicators during processing
- **Error Recovery**: Graceful error handling with helpful messages
- **Auto-scroll**: Automatically scroll to new messages
- **Keyboard Shortcuts**: Support common keyboard interactions
- **Visual Feedback**: Color-coded priorities, emojis for issue types
