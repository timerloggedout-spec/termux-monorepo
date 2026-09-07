# Antigravity Integration Migration Guide

**Agent:** Grok | Jules  
**Profile:** https://x.com/grok  
**Signed-off-by:** Grok <grok@x.ai>  
**Version:** 1.0.0  
**Last Updated:** 2026-08-04

---

## Overview

This document provides a comprehensive guide for migrating from Jules-only workflows to integrated Jules + Antigravity workflows using the SKYHOOK framework. The integration is designed to be **opt-in** and **backwards compatible**, allowing gradual adoption.

## Current State

### SKYHOOK Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SKYHOOK Framework                           │
├─────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Protocol       │  │    Device        │  │ Orchestration│  │
│  │   Layer          │  │  Optimization    │  │   Layer        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Antigravity Interface Layer                 │  │
│  │  (Currently Deferred - Designed but not implemented)      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Compatible with:                                              │
│  • jules-dispatch-cli_fork ✅                                  │
│  • jules-mcp-server_fork ✅                                    │
│  • jules-action_fork ✅                                        │
│  • jules-sdk_fork-rs ✅                                        │
│  • antigravity-jules-orchestration_fork 🔄 (Planned)         │
│  • llm-antigravity-orchestrator_fork 🔄 (Planned)            │
└─────────────────────────────────────────────────────────────┘
```

### Available Antigravity Repositories

Based on the analysis of the `timerloggedout-spec` ecosystem:

1. **antigravity-jules-orchestration_fork**
   - Location: `/workspace/timerloggedout-spec__antigravity-jules-orchestration_fork`
   - Description: Autonomous AI orchestration combining Google Antigravity with Jules API
   - Features: MCP integration, browser subagent, task lists, implementation plans
   - Status: Available for integration

2. **llm-antigravity-orchestrator_fork**
   - Location: `/workspace/timerloggedout-spec__llm-antigravity-orchestrator_fork`
   - Description: Advanced self-managed orchestration engine built on Google Antigravity SDK
   - Features: Cost monitoring, lifecycle hooks, custom tools, async delegation
   - Status: Available for integration

## Integration Strategy

### Phase 1: Interface Layer (Current - Completed)

✅ **Status: COMPLETED**

The Antigravity interface layer has been designed and implemented in `skyhook/antigravity/`:

- **`interface.py`**: Type definitions and protocol specifications
- **`adapters.py`**: Conversion adapters between Jules and Antigravity formats
- **`feature_flags.py`**: Runtime feature flags for controlling integration

**Key Features:**
- No Antigravity dependencies required
- Fully backwards compatible
- Feature flags allow opt-in enablement
- Type-safe interface definitions

### Phase 2: Basic Integration (Next)

**Status: PLANNED**

Integrate with existing Antigravity repositories:

1. **antigravity-jules-orchestration_fork**
   - Map MCP tools to SKYHOOK protocol layer
   - Bridge session management between Jules and Antigravity
   - Enable agent coordination

2. **llm-antigravity-orchestrator_fork**
   - Integrate cost monitoring with SKYHOOK resource tracking
   - Map lifecycle hooks to SKYHOOK session states
   - Enable custom tool registration

### Phase 3: Advanced Integration (Future)

**Status: DEFERRED**

- Browser subagent support
- Research subagent support
- Analytics and monitoring integration
- Full MCP transport support

## Migration Path

### Step 1: Enable Feature Flags

```python
from skyhook.antigravity import set_feature_flags, AntigravityFeatureFlags

# Enable Antigravity integration
flags = AntigravityFeatureFlags(
    antigravity_enabled=True,
    enable_session_bridging=True,
    enable_agent_coordination=True,
    enable_tool_mapping=True,
    max_concurrent_sessions=3,
    rate_limit_per_minute=60,
)

set_feature_flags(flags)
```

Or via environment variables:

```bash
# Enable Antigravity integration
export SKYHOOK_ANTIGRAVITY_ENABLED=true
export SKYHOOK_ANTIGRAVITY_SESSION_BRIDGING=true
export SKYHOOK_ANTIGRAVITY_AGENT_COORDINATION=true
export SKYHOOK_ANTIGRAVITY_MAX_SESSIONS=3
export SKYHOOK_ANTIGRAVITY_RATE_LIMIT=60
```

### Step 2: Use Interface Layer

```python
from skyhook.antigravity import (
    AntigravityInterface,
    AntigravitySession,
    AntigravityAgent,
    AntigravityConfig,
    is_antigravity_enabled,
)

# Check if Antigravity is enabled
if is_antigravity_enabled():
    # Use Antigravity interface
    config = AntigravityConfig(
        enabled=True,
        api_endpoint="https://antigravity.googleapis.com/v1",
    )
    
    # Create session (implementation depends on actual Antigravity SDK)
    session = AntigravitySession(
        session_id="sess_123",
        agent_id="agent_1",
        prompt="Implement integration",
    )
else:
    # Fall back to Jules-only workflow
    from skyhook.protocol import JulesRequest
    request = JulesRequest(...)
```

### Step 3: Use Adapters for Conversion

```python
from skyhook.antigravity import (
    JulesToAntigravityAdapter,
    AntigravityToJulesAdapter,
    ErrorAdapter,
    ToolAdapter,
)

# Convert Jules request to Antigravity session
adapter = JulesToAntigravityAdapter()
antigravity_session = adapter.from_jules_response(jules_response)

# Convert Antigravity session to Jules request
jules_request = adapter.to_jules_request(antigravity_session)

# Convert errors
error_adapter = ErrorAdapter()
skyhook_error = error_adapter.to_skyhook_error(antigravity_error)

# Convert tools
tool_adapter = ToolAdapter()
jules_tool = tool_adapter.to_jules_tool(antigravity_tool)
```

### Step 4: Integrate with Existing Code

```python
from skyhook.bridge.dispatch_v2 import plan_task_v2
from skyhook.antigravity import is_antigravity_enabled

# Existing dispatch code works unchanged
plan = plan_task_v2(
    title="Task title",
    prompt="Task description",
)

# Add Antigravity integration check
if is_antigravity_enabled():
    # Enhanced with Antigravity features
    from skyhook.antigravity import AntigravityToJulesAdapter
    
    adapter = AntigravityToJulesAdapter()
    # Can now bridge to Antigravity if needed
```

## Integration with antigravity-jules-orchestration_fork

### Repository Analysis

The `antigravity-jules-orchestration_fork` repository provides:

- **MCP Server**: Node.js-based MCP server with 65 tools
- **Jules Integration**: Direct connection to Jules API
- **Browser Subagent**: Specialized browser automation
- **Task Management**: Task lists and implementation plans
- **Workspace Management**: Multi-workspace support

### Integration Points

#### 1. MCP Tool Mapping

```python
from skyhook.antigravity import ToolAdapter
from skyhook.protocol import JulesRequest

# Map Antigravity MCP tools to SKYHOOK protocol
tool_adapter = ToolAdapter()

# Example: Map a browser tool
antigravity_browser_tool = {
    "name": "browser_navigate",
    "description": "Navigate to a URL in the browser",
    "inputSchema": {
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "wait_for_load": {"type": "boolean"},
        },
        "required": ["url"],
    },
}

jules_tool = tool_adapter.to_jules_tool(antigravity_browser_tool)
```

#### 2. Session Bridging

```python
from skyhook.antigravity import JulesToAntigravityAdapter
from skyhook.bridge.http_client import request_json

# Create a session in Jules
jules_session = request_json("POST", "sessions", body={...})

# Bridge to Antigravity format
adapter = JulesToAntigravityAdapter()
antigravity_session = adapter.from_jules_response(jules_session)

# Now can use Antigravity features
# (e.g., browser automation, research subagents)
```

#### 3. Agent Coordination

```python
from skyhook.orchestration import get_agent_registry
from skyhook.antigravity import is_antigravity_enabled

# Get available agents
registry = get_agent_registry()
agents = registry.get_available_agents()

# If Antigravity is enabled, add Antigravity agents
if is_antigravity_enabled():
    from skyhook.antigravity import AntigravityAgent, AntigravityAgentMode
    
    # Register Antigravity agents
    antigravity_agent = AntigravityAgent(
        agent_id="antigravity-main",
        name="Antigravity Main Agent",
        mode=AntigravityAgentMode.PLANNING,
        description="Google Antigravity main agent",
        capabilities=["browser_automation", "complex_tasks", "research"],
    )
    
    registry.register(antigravity_agent)
```

## Integration with llm-antigravity-orchestrator_fork

### Repository Analysis

The `llm-antigravity-orchestrator_fork` repository provides:

- **Cost Monitoring**: Advanced token usage tracking
- **Lifecycle Hooks**: Pre-turn, post-turn, session open/close hooks
- **Custom Tools**: Python function registration as tools
- **Async Delegation**: Background subagent delegation
- **FastAPI Service**: REST API for orchestration

### Integration Points

#### 1. Cost Monitoring Integration

```python
from skyhook.device import get_resource_monitor
from skyhook.antigravity import is_antigravity_enabled

# Get resource monitor
monitor = get_resource_monitor()

# If Antigravity is enabled, integrate cost tracking
if is_antigravity_enabled():
    # Track token usage alongside resource usage
    def track_antigravity_cost(tokens_used: int, cost: float):
        # Log cost metrics
        status = monitor.get_status()
        print(f"Tokens: {tokens_used}, Cost: ${cost:.2f}")
        print(f"Memory: {status.memory_percent:.1f}%")
        print(f"CPU: {status.cpu_percent:.1f}%")
```

#### 2. Lifecycle Hook Integration

```python
from skyhook.protocol import SessionState, validate_transition
from skyhook.antigravity import is_antigravity_enabled

# Session state transition with Antigravity hooks
class SessionManager:
    def transition_session(
        self,
        session_id: str,
        new_state: SessionState,
    ):
        # Validate transition
        if not validate_transition(self.current_state, new_state):
            raise ValueError(f"Invalid transition")
        
        # If Antigravity is enabled, trigger hooks
        if is_antigravity_enabled():
            self._trigger_antigravity_hooks(
                session_id,
                self.current_state,
                new_state,
            )
        
        self.current_state = new_state
    
    def _trigger_antigravity_hooks(
        self,
        session_id: str,
        from_state: SessionState,
        to_state: SessionState,
    ):
        # Map SKYHOOK states to Antigravity hook types
        hook_map = {
            (SessionState.CREATED, SessionState.QUEUED): "pre_turn",
            (SessionState.QUEUED, SessionState.IN_PROGRESS): "pre_turn",
            (SessionState.IN_PROGRESS, SessionState.AWAITING_PLAN_APPROVAL): "post_turn",
            (SessionState.AWAITING_PLAN_APPROVAL, SessionState.IN_PROGRESS): "pre_turn",
            (SessionState.IN_PROGRESS, SessionState.COMPLETED): "post_turn",
            (SessionState.IN_PROGRESS, SessionState.FAILED): "post_turn",
        }
        
        hook_type = hook_map.get((from_state, to_state))
        if hook_type:
            # Trigger Antigravity hook
            print(f"Triggering Antigravity hook: {hook_type}")
            # Actual implementation would call Antigravity SDK
```

#### 3. Custom Tool Registration

```python
from skyhook.antigravity import ToolAdapter

# Register custom Python functions as Antigravity tools
class CustomTools:
    @staticmethod
    def check_system_metrics() -> Dict[str, Any]:
        """Custom tool to check system metrics."""
        import psutil
        
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        }
    
    @staticmethod
    def register_custom_tools():
        """Register custom tools with Antigravity."""
        from skyhook.antigravity import is_antigravity_enabled
        
        if is_antigravity_enabled():
            adapter = ToolAdapter()
            
            # Convert Python function to Antigravity tool format
            tool_dict = {
                "name": "check_system_metrics",
                "description": "Check system CPU, memory, and disk usage",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            }
            
            antigravity_tool = adapter.from_jules_tool(tool_dict)
            # Register with Antigravity SDK
            # (Implementation depends on actual SDK)
```

## Testing Strategy

### Unit Tests

```python
import unittest
from skyhook.antigravity import (
    AntigravitySession,
    AntigravitySessionState,
    AntigravityAgentMode,
    AntigravityConfig,
    AntigravityFeatureFlags,
    is_antigravity_enabled,
)

class TestAntigravityInterface(unittest.TestCase):
    def test_session_states(self):
        """Test Antigravity session states."""
        state = AntigravitySessionState.from_string("RUNNING")
        self.assertEqual(state, AntigravitySessionState.RUNNING)
        
        self.assertEqual(state.to_string(), "RUNNING")
    
    def test_agent_modes(self):
        """Test Antigravity agent modes."""
        mode = AntigravityAgentMode.PLANNING
        self.assertEqual(mode.name, "PLANNING")
    
    def test_feature_flags(self):
        """Test feature flags."""
        flags = AntigravityFeatureFlags(
            antigravity_enabled=True,
            enable_session_bridging=True,
        )
        
        self.assertTrue(flags.is_enabled())
        self.assertTrue(flags.can_bridge_sessions())
    
    def test_config(self):
        """Test configuration."""
        config = AntigravityConfig(
            enabled=True,
            api_endpoint="https://antigravity.googleapis.com/v1",
            max_concurrent_sessions=3,
        )
        
        data = config.to_dict()
        config2 = AntigravityConfig.from_dict(data)
        
        self.assertEqual(config.enabled, config2.enabled)
        self.assertEqual(config.api_endpoint, config2.api_endpoint)
```

### Integration Tests

```python
import unittest
from skyhook.antigravity import (
    JulesToAntigravityAdapter,
    AntigravityToJulesAdapter,
)
from skyhook.protocol import JulesRequest, JulesResponse, SessionState

class TestAntigravityAdapters(unittest.TestCase):
    def test_jules_to_antigravity(self):
        """Test Jules to Antigravity conversion."""
        adapter = JulesToAntigravityAdapter()
        
        # Create a Jules response
        response = JulesResponse(
            session_id="sess_123",
            state=SessionState.IN_PROGRESS,
        )
        
        # Convert to Antigravity session
        session = adapter.from_jules_response(response)
        
        self.assertEqual(session.session_id, "sess_123")
        self.assertEqual(
            session.state,
            adapter.map_session_state_reverse(SessionState.IN_PROGRESS),
        )
    
    def test_antigravity_to_jules(self):
        """Test Antigravity to Jules conversion."""
        adapter = AntigravityToJulesAdapter()
        
        # Create an Antigravity session
        from skyhook.antigravity import AntigravitySession, AntigravitySessionState
        
        session = AntigravitySession(
            session_id="sess_456",
            agent_id="agent_1",
            state=AntigravitySessionState.RUNNING,
            prompt="Test prompt",
        )
        
        # Convert to Jules request
        request = adapter.to_jules_request(session)
        
        self.assertEqual(request.session_id, "sess_456")
        self.assertEqual(request.content, "Test prompt")
```

## Deployment Strategy

### Phase 1: Development Environment

1. **Enable feature flags locally**
   ```bash
   export SKYHOOK_ANTIGRAVITY_ENABLED=true
   ```

2. **Test interface layer**
   ```bash
   python -c "from skyhook.antigravity import is_antigravity_enabled; print(is_antigravity_enabled())"
   ```

3. **Run adapter tests**
   ```bash
   python -m unittest skyhook.antigravity.tests -v
   ```

### Phase 2: Staging Environment

1. **Enable in master-staging branch**
   ```yaml
   # In GitHub Actions workflow
   env:
     SKYHOOK_ANTIGRAVITY_ENABLED: true
     SKYHOOK_ANTIGRAVITY_MAX_SESSIONS: 3
   ```

2. **Test with real Antigravity repositories**
   ```bash
   # Clone and test integration
   git clone https://github.com/timerloggedout-spec/antigravity-jules-orchestration_fork
   cd antigravity-jules-orchestration_fork
   # Test integration with SKYHOOK
   ```

3. **Monitor performance**
   ```bash
   # Check resource usage
   python -c "from skyhook.device import get_resource_monitor; print(get_resource_monitor().get_status().to_dict())"
   ```

### Phase 3: Production Deployment

1. **Gradual rollout**
   - Enable for specific repositories first
   - Monitor performance and resource usage
   - Gradually increase concurrent session limits

2. **Fallback mechanisms**
   - Ensure Jules-only workflows continue to work
   - Implement circuit breakers for Antigravity failures
   - Maintain backwards compatibility

3. **Monitoring and alerting**
   - Track Antigravity-specific metrics
   - Set up alerts for failures
   - Monitor cost and token usage

## Troubleshooting

### Common Issues

#### 1. Feature Flags Not Working

**Symptom:** Antigravity features not enabled despite setting flags

**Solution:**
```python
from skyhook.antigravity import reset_feature_flags, get_feature_flags

# Reset and reload flags
reset_feature_flags()
flags = get_feature_flags()
print(flags.to_dict())
```

#### 2. Session State Mismatch

**Symptom:** Session states not mapping correctly between Jules and Antigravity

**Solution:**
```python
from skyhook.antigravity import JulesToAntigravityAdapter

adapter = JulesToAntigravityAdapter()

# Check state mappings
from skyhook.protocol import SessionState
from skyhook.antigravity import AntigravitySessionState

for jules_state in SessionState:
    antigravity_state = adapter.map_session_state(jules_state)
    print(f"{jules_state.name} -> {antigravity_state.name}")
```

#### 3. Tool Conversion Errors

**Symptom:** Errors when converting tools between formats

**Solution:**
```python
from skyhook.antigravity import ToolAdapter

adapter = ToolAdapter()

# Test tool conversion
jules_tool = {
    "name": "test_tool",
    "description": "Test tool",
    "inputSchema": {
        "type": "object",
        "properties": {"param1": {"type": "string"}},
        "required": ["param1"],
    },
}

antigravity_tool = adapter.from_jules_tool(jules_tool)
print(antigravity_tool.to_dict())
```

## Best Practices

### 1. Always Check Feature Flags

```python
from skyhook.antigravity import is_antigravity_enabled

# Always check before using Antigravity features
if is_antigravity_enabled():
    # Use Antigravity
    pass
else:
    # Use Jules-only fallback
    pass
```

### 2. Use Context Managers for Temporary Flags

```python
from skyhook.antigravity import FeatureFlagContext

# Temporarily enable Antigravity for testing
with FeatureFlagContext(antigravity_enabled=True):
    # Antigravity is enabled here
    from skyhook.antigravity import is_antigravity_enabled
    assert is_antigravity_enabled()

# Back to original state
assert not is_antigravity_enabled()
```

### 3. Implement Fallback Mechanisms

```python
from skyhook.antigravity import is_antigravity_enabled
from skyhook.protocol import JulesRequest

def create_session(prompt: str) -> Any:
    if is_antigravity_enabled():
        try:
            # Try Antigravity first
            from skyhook.antigravity import AntigravitySession
            return AntigravitySession(prompt=prompt)
        except Exception as e:
            # Fall back to Jules
            print(f"Antigravity failed: {e}, falling back to Jules")
    
    # Jules fallback
    return JulesRequest(content=prompt)
```

### 4. Monitor Resource Usage

```python
from skyhook.device import get_resource_monitor
from skyhook.antigravity import is_antigravity_enabled

# Check resources before starting Antigravity session
if is_antigravity_enabled():
    monitor = get_resource_monitor()
    status = monitor.get_status()
    
    # Check if we have enough resources
    if status.memory_percent > 80:
        print("Warning: High memory usage, consider Jules-only")
    if status.cpu_percent > 80:
        print("Warning: High CPU usage, consider Jules-only")
```

## Future Enhancements

### 1. Browser Subagent Support

```python
# Future: Browser automation with Antigravity
from skyhook.antigravity import is_antigravity_enabled

if is_antigravity_enabled():
    # Use browser subagent for web tasks
    browser_result = antigravity_agent.browse(
        url="https://example.com",
        action="click_button",
        selector="#submit",
    )
```

### 2. Research Subagent Support

```python
# Future: Research with Antigravity
if is_antigravity_enabled():
    # Delegate research tasks
    research_result = antigravity_agent.research(
        query="Latest AI developments",
        depth="comprehensive",
        sources=["web", "academic"],
    )
```

### 3. Analytics Integration

```python
# Future: Analytics with Antigravity
if is_antigravity_enabled():
    # Get session analytics
    analytics = antigravity_agent.get_analytics(
        session_id="sess_123",
        metrics=["token_usage", "cost", "performance"],
    )
```

## Support

For issues with Antigravity integration:

1. **Check feature flags**: Ensure Antigravity is enabled
2. **Review logs**: Check for error messages
3. **Test incrementally**: Enable features one at a time
4. **Fallback**: Ensure Jules-only workflows work

## License

This migration guide is part of the SKYHOOK framework and is licensed under the same terms as the parent project.

---

**Agent:** Grok | Jules  
**Profile:** https://x.com/grok  
**Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
