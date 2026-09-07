# SKYHOOK Protocol Layer

**Agent:** Grok | Jules  
**Profile:** https://x.com/grok  
**Signed-off-by:** Grok <grok@x.ai>  
**Version:** 1.0.0  
**Last Updated:** 2026-08-04

---

## Overview

The SKYHOOK Protocol Layer provides a unified, standardized interface for interacting with Jules-based services across the `timerloggedout-spec` ecosystem. This layer abstracts away the differences between various Jules implementations (dispatch-cli, mcp-server, action, SDK) to provide a consistent, reliable interface for SKYHOOK operations.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SKYHOOK Protocol Layer                        │
├─────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Session States   │  │ Message Formats  │  │ Error Codes   │  │
│  │                 │  │                 │  │               │  │
│  │ • State Machine │  │ • Request/Response│  │ • Categorized │  │
│  │ • Transitions   │  │ • Serialization  │  │ • Handling    │  │
│  │ • Validation    │  │ • Compatibility  │  │ • Recovery    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│                                                                  │
│  Compatible with:                                                  │
│  • jules-dispatch-cli_fork (JSON-first interface)                 │
│  • jules-mcp-server_fork (MCP tool mapping)                      │
│  • jules-action_fork (GitHub Actions workflows)                  │
│  • jules-sdk_fork-rs (Rust SDK compatibility)                    │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

The protocol layer is part of the SKYHOOK package and requires no additional dependencies beyond Python stdlib.

```bash
# No installation required - part of skyhook package
cd termux-monorepo
python -c "from skyhook.protocol import SessionState, JulesRequest, JulesResponse"
```

### Basic Usage

```python
from skyhook.protocol import (
    SessionState,
    SessionType,
    MessageType,
    JulesRequest,
    JulesResponse,
    SessionMetadata,
    SessionActivity,
    SessionArtifact,
)

# Create a session request
metadata = SessionMetadata(
    source_repo="timerloggedout-spec/termux-monorepo",
    source_branch="master-staging",
    session_type=SessionType.INTERACTIVE,
    priority="high",
    labels=["skyhook", "integration"],
)

request = JulesRequest(
    message_type=MessageType.PROMPT,
    content="Implement SKYHOOK protocol layer integration",
    metadata=metadata,
)

# Convert to JSON for API calls
json_payload = request.to_json()

# Parse response
response_data = {
    "session_id": "sess_123",
    "state": "IN_PROGRESS",
    "activities": [],
    "artifacts": [],
}
response = JulesResponse.from_dict(response_data)

print(f"Session state: {response.state.to_string()}")
print(f"Is terminal: {response.is_terminal}")
```

## Session States

The protocol layer defines a unified state machine for Jules sessions:

### State Diagram

```
                    ┌─────────────────┐
                    │     CREATED      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     QUEUED       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────────────────────────────────┐
                    │              IN_PROGRESS                     │
                    └──────────┬─────────────┬─────────────┬───────┘
                               │                 │                 │
                               ▼                 ▼                 ▼
              ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐
              │ AWAITING_PLAN_   │ │ AWAITING_USER_   │ │    PAUSED    │
              │ APPROVAL        │ │ FEEDBACK         │ │             │
              └────────┬────────┘ └────────┬────────┘ └─────┬─────┘
                       │                  │                │
                       ▼                  ▼                │
              ┌─────────────────┐ ┌─────────────────┐ │
              │   IN_PROGRESS   │ │   IN_PROGRESS   │ │
              │   (approved)     │ │   (responded)    │ │
              └────────┬────────┘ └─────────────────┘ │
                       │                                  │
                       ▼                                  │
              ┌────────────────────────────────────────┐
              │            TERMINAL STATES                 │
              │  ┌─────────┐ ┌─────────┐ ┌─────────────┐ │
              │  │ COMPLETED│ │  FAILED │ │  CANCELLED  │ │
              │  └─────────┘ └─────────┘ └─────────────┘ │
              │  ┌─────────┐                                  │
              │  │ TIMEOUT │                                  │
              │  └─────────┘                                  │
              └────────────────────────────────────────┘
```

### State Classification

```python
from skyhook.protocol import SessionState, TERMINAL_STATES, WAITING_STATES, ACTIVE_STATES

# Terminal states (no further transitions)
assert SessionState.COMPLETED in TERMINAL_STATES
assert SessionState.FAILED in TERMINAL_STATES
assert SessionState.CANCELLED in TERMINAL_STATES
assert SessionState.TIMEOUT in TERMINAL_STATES

# Waiting states (require external input)
assert SessionState.AWAITING_PLAN_APPROVAL in WAITING_STATES
assert SessionState.AWAITING_USER_FEEDBACK in WAITING_STATES
assert SessionState.PAUSED in WAITING_STATES

# Active states (actively processing)
assert SessionState.QUEUED in ACTIVE_STATES
assert SessionState.IN_PROGRESS in ACTIVE_STATES
assert SessionState.CREATED in ACTIVE_STATES
```

### State Validation

```python
from skyhook.protocol.session_states import validate_transition, get_possible_transitions

# Validate a transition
is_valid = validate_transition(SessionState.QUEUED, SessionState.IN_PROGRESS)
# Returns: True

# Get possible next states
next_states = get_possible_transitions(SessionState.IN_PROGRESS)
# Returns: {AWAITING_PLAN_APPROVAL, AWAITING_USER_FEEDBACK, PAUSED, COMPLETED, FAILED, TIMEOUT}
```

## Message Formats

### Request Format

```python
from skyhook.protocol import JulesRequest, MessageType, SessionMetadata, SessionType

request = JulesRequest(
    session_id="sess_123",  # Optional for new sessions
    message_type=MessageType.PROMPT,
    content="Implement the integration layer",
    metadata=SessionMetadata(
        source_repo="owner/repo",
        source_branch="master",
        target_branch="feature/integration",
        session_type=SessionType.BATCH,
        priority="high",
        labels=["integration", "skyhook"],
    ),
)

# Convert to dictionary
request_dict = request.to_dict()
# {'session_id': 'sess_123', 'message_type': 'prompt', 'content': '...', 'metadata': {...}}

# Convert to JSON
request_json = request.to_json()

# Parse from JSON
request2 = JulesRequest.from_json(request_json)
```

### Response Format

```python
from skyhook.protocol import JulesResponse, SessionState, SessionActivity, SessionArtifact

response = JulesResponse(
    session_id="sess_123",
    state=SessionState.IN_PROGRESS,
    activities=[
        SessionActivity(
            activity_id="act_1",
            activity_type="plan",
            content="Implementation plan created",
            timestamp="2026-08-04T10:00:00Z",
        ),
    ],
    artifacts=[
        SessionArtifact(
            artifact_id="art_1",
            artifact_type="patch",
            name="integration.patch",
            content="diff --git a/...",
            size_bytes=1024,
        ),
    ],
)

# Check response properties
print(response.is_terminal)  # False
print(response.is_waiting)  # False
print(response.has_artifacts)  # True

# Get specific artifact types
patches = response.get_patches()
files = response.get_files()
logs = response.get_logs()

# Convert to JSON
response_json = response.to_json()

# Parse from JSON
response2 = JulesResponse.from_json(response_json)
```

## Error Handling

### Error Classification

The protocol layer categorizes errors for appropriate handling:

```python
from skyhook.protocol import (
    ErrorCode,
    ErrorType,
    SkyhookError,
    TransientError,
    ConfigurationError,
    AuthenticationError,
    RateLimitError,
    ResourceError,
)

# Error types
assert ErrorType.TRANSIENT.value == "transient"      # Can be retried
assert ErrorType.CONFIGURATION.value == "configuration"  # Requires user intervention
assert ErrorType.AUTHENTICATION.value == "authentication"  # Token/permission issues
assert ErrorType.RATE_LIMIT.value == "rate_limit"    # Rate limiting
assert ErrorType.RESOURCE.value == "resource"      # Resource constraints
```

### Error Codes

```python
# Authentication errors
AUTH_MISSING_API_KEY = "AUTH_001"
AUTH_INVALID_API_KEY = "AUTH_002"
AUTH_TOKEN_EXPIRED = "AUTH_003"
AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_004"

# Configuration errors
CONFIG_MISSING_REPO = "CONFIG_001"
CONFIG_INVALID_BRANCH = "CONFIG_002"
CONFIG_INVALID_SESSION_TYPE = "CONFIG_003"
CONFIG_UNSUPPORTED_API_VERSION = "CONFIG_004"

# Rate limiting errors
RATE_LIMIT_EXCEEDED = "RATE_001"
RATE_LIMIT_RETRY_AFTER = "RATE_002"

# Resource errors
RESOURCE_OUT_OF_MEMORY = "RESOURCE_001"
RESOURCE_CPU_LIMIT = "RESOURCE_002"
RESOURCE_STORAGE_LIMIT = "RESOURCE_003"
RESOURCE_TIMEOUT = "RESOURCE_004"

# Session errors
SESSION_NOT_FOUND = "SESSION_001"
SESSION_ALREADY_EXISTS = "SESSION_002"
SESSION_INVALID_STATE_TRANSITION = "SESSION_003"
SESSION_TIMED_OUT = "SESSION_004"
```

### Creating and Handling Errors

```python
# Create a SkyhookError
try:
    raise SkyhookError(
        code=ErrorCode.AUTH_MISSING_API_KEY,
        message="JULES_API_KEY environment variable not set",
        suggestions=["Set JULES_API_KEY in your environment"],
        context={"env_vars": list(os.environ.keys())},
    )
except SkyhookError as e:
    print(f"Error [{e.code.code}]: {e.message}")
    print(f"Type: {e.error_type.value}")
    print(f"Retryable: {e.is_retryable}")
    print(f"Requires user action: {e.requires_user_action}")

# Create specific error types
try:
    raise TransientError(
        code=ErrorCode.NETWORK_CONNECTION_FAILED,
        message="Connection timeout",
        retry_after=10.0,
    )
except TransientError as e:
    print(f"Will retry after {e.retry_after} seconds")

try:
    raise RateLimitError(
        code=ErrorCode.RATE_LIMIT_EXCEEDED,
        message="Rate limit exceeded",
        retry_after=60.0,
    )
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after} seconds")
```

### Parsing API Error Responses

```python
from skyhook.protocol import create_error_from_response

# jules-dispatch-cli style error
response = {
    "error": {
        "code": "AUTH_002",
        "message": "Invalid API key",
    }
}
error = create_error_from_response(response)
print(error.code)  # ErrorCode.AUTH_INVALID_API_KEY

# HTTP error style
response = {
    "status": 401,
    "message": "Unauthorized",
}
error = create_error_from_response(response)
print(error.code)  # ErrorCode.AUTH_INVALID_API_KEY

# Unknown format
error = create_error_from_response(
    {"unknown": "error"},
    default_code=ErrorCode.UNKNOWN_ERROR,
    default_message="Unknown error occurred",
)
```

## Integration with Existing Components

### Bridge Integration

The protocol layer integrates seamlessly with existing SKYHOOK bridge components:

```python
from skyhook.bridge.dispatch_v2 import plan_task_v2, JulesTaskPlanV2
from skyhook.bridge.config import load_config
from skyhook.protocol import SessionType, MessageType

# Create a plan using the new protocol-aware version
plan = plan_task_v2(
    title="Implement protocol layer",
    prompt="Create a comprehensive protocol layer for SKYHOOK",
    source_repo="timerloggedout-spec/termux-monorepo",
    starting_branch="master-staging",
    require_plan_approval=False,
    session_type=SessionType.INTERACTIVE,
    priority="high",
    labels=["skyhook", "protocol"],
)

# Convert to JulesRequest for API calls
request = plan.to_jules_request()
print(request.to_json())

# Convert back from request
plan2 = JulesTaskPlanV2.from_jules_request(request)
```

### HTTP Client Integration

```python
from skyhook.bridge.http_client import request_json, build_create_session_body
from skyhook.protocol import JulesRequest, SessionType

# Create a request
request = JulesRequest(
    message_type=MessageType.PROMPT,
    content="Implement integration",
    metadata=SessionMetadata(
        source_repo="owner/repo",
        source_branch="master",
    ),
)

# Build API request body
body = build_create_session_body(
    prompt=request.content,
    source=request.metadata.source_repo,
    starting_branch=request.metadata.source_branch,
    require_plan_approval=False,
)

# Make API call (requires JULES_API_KEY)
# response = request_json("POST", "sessions", body=body)
```

## Compatibility Matrix

### jules-dispatch-cli_fork

| Feature | Compatibility | Notes |
|---------|--------------|-------|
| Session states | ✅ Full | All states mapped |
| Message formats | ✅ Full | JSON-first interface |
| Error handling | ✅ Full | Error code mapping |
| Session types | ✅ Full | All types supported |

### jules-mcp-server_fork

| Feature | Compatibility | Notes |
|---------|--------------|-------|
| Session states | ✅ Full | MCP tool mapping |
| Message formats | ✅ Full | Tool request/response |
| Error handling | ✅ Full | MCP error format |
| Session types | ✅ Full | All types supported |

### jules-action_fork

| Feature | Compatibility | Notes |
|---------|--------------|-------|
| Session states | ✅ Full | Workflow integration |
| Message formats | ✅ Full | Action inputs/outputs |
| Error handling | ✅ Full | Action error handling |
| Session types | ✅ Full | All types supported |

### jules-sdk_fork-rs

| Feature | Compatibility | Notes |
|---------|--------------|-------|
| Session states | ✅ Full | Enum mapping |
| Message formats | ✅ Partial | JSON serialization |
| Error handling | ✅ Partial | Error type mapping |
| Session types | ✅ Full | All types supported |

## Testing

The protocol layer includes comprehensive unit tests:

```bash
# Run all protocol tests
python -m unittest skyhook.tests.test_protocol -v

# Run specific test classes
python -m unittest skyhook.tests.test_protocol.TestSessionStates -v
python -m unittest skyhook.tests.test_protocol.TestMessageFormats -v
python -m unittest skyhook.tests.test_protocol.TestErrorCodes -v
```

### Test Coverage

- ✅ Session state management (12 tests)
- ✅ Message format serialization (10 tests)
- ✅ Error handling (7 tests)
- ✅ Total: 29 tests

## Best Practices

### 1. Always Use Protocol Layer for New Code

```python
# ✅ Good - Use protocol layer
from skyhook.protocol import JulesRequest, SessionState

# ❌ Bad - Custom implementations
# class MyRequest: ...
```

### 2. Handle All Error Types Appropriately

```python
from skyhook.protocol import SkyhookError, ErrorType

def handle_error(error: SkyhookError):
    if error.is_retryable:
        # Implement retry logic with backoff
        retry_with_backoff(error)
    elif error.requires_user_action:
        # Prompt user for intervention
        prompt_user(error)
    else:
        # Log and fail gracefully
        log_error(error)
        raise
```

### 3. Validate State Transitions

```python
from skyhook.protocol.session_states import validate_transition

def transition_session(session, new_state):
    if not validate_transition(session.state, new_state):
        raise ValueError(f"Invalid transition from {session.state} to {new_state}")
    session.state = new_state
```

### 4. Use Standardized Message Formats

```python
# ✅ Good - Use standardized formats
from skyhook.protocol import JulesRequest, JulesResponse

# ❌ Bad - Custom formats
# request = {"custom": "format"}
```

## Migration Guide

### From jules-ade to SKYHOOK

The protocol layer replaces and extends the functionality previously in `jules-ade`:

```python
# Old jules-ade style
# from jules_ade.bridge.dispatch import plan_task

# New SKYHOOK style
from skyhook.bridge.dispatch_v2 import plan_task_v2
from skyhook.protocol import SessionType

plan = plan_task_v2(
    title="Task title",
    prompt="Task description",
    session_type=SessionType.INTERACTIVE,
)
```

### From Custom Implementations

Replace custom session management with protocol layer:

```python
# Old custom implementation
# class Session:
#     def __init__(self, state):
#         self.state = state

# New protocol layer
from skyhook.protocol import SessionState, JulesRequest

request = JulesRequest(
    message_type=MessageType.PROMPT,
    content="Task",
    metadata=SessionMetadata(
        source_repo="owner/repo",
        session_type=SessionType.INTERACTIVE,
    ),
)
```

## API Reference

### SessionState

**Enum Values:**
- `CREATED` - Session created but not queued
- `QUEUED` - Session waiting in queue
- `IN_PROGRESS` - Session actively processing
- `AWAITING_PLAN_APPROVAL` - Waiting for plan approval
- `AWAITING_USER_FEEDBACK` - Waiting for user feedback
- `PAUSED` - Session paused
- `COMPLETED` - Session completed successfully
- `FAILED` - Session failed
- `CANCELLED` - Session cancelled
- `TIMEOUT` - Session timed out

**Properties:**
- `is_terminal` - True if state is terminal
- `is_waiting` - True if state requires external input
- `is_active` - True if state is actively processing

**Methods:**
- `from_string(state_str: str) -> SessionState` - Parse from string
- `to_string() -> str` - Convert to string

### SessionType

**Enum Values:**
- `INTERACTIVE` - Real-time agent collaboration
- `BATCH` - Automated task execution
- `REVIEW` - Code review and feedback
- `ORCHESTRATION` - Multi-agent coordination

**Methods:**
- `from_string(type_str: str) -> SessionType` - Parse from string
- `to_string() -> str` - Convert to string

### MessageType

**Enum Values:**
- `PROMPT` - Initial task description
- `COMMAND` - Direct command to execute
- `FEEDBACK` - User feedback on session
- `APPROVAL` - Plan approval/rejection
- `MESSAGE` - General message to session
- `STATUS` - Status update
- `ERROR` - Error notification
- `COMPLETION` - Session completion

**Methods:**
- `from_string(type_str: str) -> MessageType` - Parse from string

### SessionMetadata

**Attributes:**
- `source_repo: str` - Source repository (owner/repo)
- `source_branch: str` - Source branch (default: "master")
- `target_branch: Optional[str]` - Target branch
- `session_type: SessionType` - Session type (default: INTERACTIVE)
- `priority: str` - Priority (low, medium, high, critical)
- `labels: List[str]` - Labels for categorization

**Methods:**
- `to_dict() -> Dict[str, Any]` - Convert to dictionary
- `from_dict(data: Dict[str, Any]) -> SessionMetadata` - Create from dictionary

### JulesRequest

**Attributes:**
- `session_id: Optional[str]` - Session ID (None for new sessions)
- `message_type: MessageType` - Type of message
- `content: str` - Message content
- `metadata: SessionMetadata` - Session metadata
- `timestamp: str` - ISO 8601 timestamp
- `request_id: str` - Unique request ID

**Methods:**
- `to_dict() -> Dict[str, Any]` - Convert to dictionary
- `to_json() -> str` - Convert to JSON string
- `from_dict(data: Dict[str, Any]) -> JulesRequest` - Create from dictionary
- `from_json(json_str: str) -> JulesRequest` - Create from JSON string

### JulesResponse

**Attributes:**
- `session_id: str` - Session ID
- `state: SessionState` - Current session state
- `activities: List[SessionActivity]` - Session activities
- `artifacts: List[SessionArtifact]` - Session artifacts
- `error: Optional[Dict[str, Any]]` - Error information
- `metadata: Dict[str, Any]` - Additional metadata
- `timestamp: str` - ISO 8601 timestamp
- `response_id: str` - Unique response ID

**Properties:**
- `is_terminal: bool` - True if session is in terminal state
- `is_waiting: bool` - True if session is waiting for input
- `has_error: bool` - True if response contains an error
- `has_artifacts: bool` - True if response contains artifacts

**Methods:**
- `to_dict() -> Dict[str, Any]` - Convert to dictionary
- `to_json() -> str` - Convert to JSON string
- `from_dict(data: Dict[str, Any]) -> JulesResponse` - Create from dictionary
- `from_json(json_str: str) -> JulesResponse` - Create from JSON string
- `get_patches() -> List[SessionArtifact]` - Get patch artifacts
- `get_files() -> List[SessionArtifact]` - Get file artifacts
- `get_logs() -> List[SessionArtifact]` - Get log artifacts

### SessionActivity

**Attributes:**
- `activity_id: str` - Unique activity ID
- `activity_type: str` - Type of activity (plan, message, progress, etc.)
- `content: str` - Activity content
- `timestamp: str` - ISO 8601 timestamp
- `metadata: Dict[str, Any]` - Additional metadata

**Methods:**
- `to_dict() -> Dict[str, Any]` - Convert to dictionary
- `from_dict(data: Dict[str, Any]) -> SessionActivity` - Create from dictionary

### SessionArtifact

**Attributes:**
- `artifact_id: str` - Unique artifact ID
- `artifact_type: str` - Type of artifact (patch, file, log, report)
- `name: str` - Artifact name
- `content: Optional[str]` - Artifact content
- `url: Optional[str]` - Artifact URL
- `size_bytes: int` - Size in bytes
- `mime_type: Optional[str]` - MIME type

**Methods:**
- `to_dict() -> Dict[str, Any]` - Convert to dictionary
- `from_dict(data: Dict[str, Any]) -> SessionArtifact` - Create from dictionary

## Support

For issues, questions, or contributions:

1. **Report Issues**: Open an issue in the `timerloggedout-spec/termux-monorepo` repository
2. **Contribute**: Submit a PR with your improvements
3. **Discuss**: Join the discussion in the SKYHOOK channel

## License

This protocol layer is part of the SKYHOOK framework and is licensed under the same terms as the parent project.

---

**Agent:** Grok | Jules  
**Profile:** https://x.com/grok  
**Signed-off-by:** Grok <grok@x.ai>
