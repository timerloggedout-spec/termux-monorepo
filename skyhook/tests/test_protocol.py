"""Tests for SKYHOOK protocol layer.

Agent: Grok | Jules
Profile: https://x.com/grok
Signed-off-by: Grok <grok@x.ai>
"""

from __future__ import annotations

import unittest
import json
from datetime import datetime

from skyhook.protocol import (
    SessionState,
    SessionType,
    TERMINAL_STATES,
    WAITING_STATES,
    ACTIVE_STATES,
    JulesRequest,
    JulesResponse,
    SessionActivity,
    SessionArtifact,
    MessageType,
    SkyhookError,
    ErrorCode,
    ErrorType,
    TransientError,
    ConfigurationError,
    AuthenticationError,
    RateLimitError,
    ResourceError,
    create_error_from_response,
)
from skyhook.protocol.session_states import validate_transition, get_possible_transitions


class TestSessionStates(unittest.TestCase):
    """Test session state management."""
    
    def test_session_state_enum(self):
        """Test SessionState enum values."""
        self.assertEqual(SessionState.QUEUED.value, 1)
        self.assertEqual(SessionState.IN_PROGRESS.value, 2)
        self.assertEqual(SessionState.COMPLETED.value, 6)
    
    def test_from_string(self):
        """Test SessionState.from_string method."""
        self.assertEqual(
            SessionState.from_string("QUEUED"),
            SessionState.QUEUED
        )
        self.assertEqual(
            SessionState.from_string("COMPLETED"),
            SessionState.COMPLETED
        )
        self.assertEqual(
            SessionState.from_string("unknown"),
            SessionState.IN_PROGRESS  # Default
        )
    
    def test_to_string(self):
        """Test SessionState.to_string method."""
        self.assertEqual(SessionState.QUEUED.to_string(), "QUEUED")
        self.assertEqual(SessionState.COMPLETED.to_string(), "COMPLETED")
    
    def test_terminal_states(self):
        """Test terminal state classification."""
        self.assertIn(SessionState.COMPLETED, TERMINAL_STATES)
        self.assertIn(SessionState.FAILED, TERMINAL_STATES)
        self.assertIn(SessionState.CANCELLED, TERMINAL_STATES)
        self.assertIn(SessionState.TIMEOUT, TERMINAL_STATES)
        
        self.assertNotIn(SessionState.QUEUED, TERMINAL_STATES)
        self.assertNotIn(SessionState.IN_PROGRESS, TERMINAL_STATES)
    
    def test_is_terminal(self):
        """Test is_terminal property."""
        self.assertTrue(SessionState.COMPLETED.is_terminal)
        self.assertTrue(SessionState.FAILED.is_terminal)
        self.assertFalse(SessionState.QUEUED.is_terminal)
        self.assertFalse(SessionState.IN_PROGRESS.is_terminal)
    
    def test_waiting_states(self):
        """Test waiting state classification."""
        self.assertIn(SessionState.AWAITING_PLAN_APPROVAL, WAITING_STATES)
        self.assertIn(SessionState.AWAITING_USER_FEEDBACK, WAITING_STATES)
        self.assertIn(SessionState.PAUSED, WAITING_STATES)
    
    def test_is_waiting(self):
        """Test is_waiting property."""
        self.assertTrue(SessionState.AWAITING_PLAN_APPROVAL.is_waiting)
        self.assertFalse(SessionState.QUEUED.is_waiting)
    
    def test_active_states(self):
        """Test active state classification."""
        self.assertIn(SessionState.QUEUED, ACTIVE_STATES)
        self.assertIn(SessionState.IN_PROGRESS, ACTIVE_STATES)
        self.assertIn(SessionState.CREATED, ACTIVE_STATES)
    
    def test_is_active(self):
        """Test is_active property."""
        self.assertTrue(SessionState.QUEUED.is_active)
        self.assertTrue(SessionState.IN_PROGRESS.is_active)
        self.assertFalse(SessionState.COMPLETED.is_active)
    
    def test_validate_transition(self):
        """Test state transition validation."""
        # Valid transitions
        self.assertTrue(validate_transition(
            SessionState.CREATED, SessionState.QUEUED
        ))
        self.assertTrue(validate_transition(
            SessionState.QUEUED, SessionState.IN_PROGRESS
        ))
        self.assertTrue(validate_transition(
            SessionState.IN_PROGRESS, SessionState.AWAITING_PLAN_APPROVAL
        ))
        self.assertTrue(validate_transition(
            SessionState.AWAITING_PLAN_APPROVAL, SessionState.IN_PROGRESS
        ))
        self.assertTrue(validate_transition(
            SessionState.IN_PROGRESS, SessionState.COMPLETED
        ))
        
        # Invalid transitions
        self.assertFalse(validate_transition(
            SessionState.COMPLETED, SessionState.QUEUED
        ))
        self.assertFalse(validate_transition(
            SessionState.QUEUED, SessionState.COMPLETED
        ))
    
    def test_get_possible_transitions(self):
        """Test getting possible transitions."""
        transitions = get_possible_transitions(SessionState.IN_PROGRESS)
        
        self.assertIn(SessionState.AWAITING_PLAN_APPROVAL, transitions)
        self.assertIn(SessionState.AWAITING_USER_FEEDBACK, transitions)
        self.assertIn(SessionState.PAUSED, transitions)
        self.assertIn(SessionState.COMPLETED, transitions)
        self.assertIn(SessionState.FAILED, transitions)
        
        # Terminal states have no transitions
        self.assertEqual(
            len(get_possible_transitions(SessionState.COMPLETED)),
            0
        )


class TestSessionType(unittest.TestCase):
    """Test SessionType enum."""
    
    def test_from_string(self):
        """Test SessionType.from_string method."""
        self.assertEqual(
            SessionType.from_string("INTERACTIVE"),
            SessionType.INTERACTIVE
        )
        self.assertEqual(
            SessionType.from_string("BATCH"),
            SessionType.BATCH
        )
        self.assertEqual(
            SessionType.from_string("unknown"),
            SessionType.INTERACTIVE  # Default
        )


class TestMessageFormats(unittest.TestCase):
    """Test message format classes."""
    
    def test_message_type_enum(self):
        """Test MessageType enum."""
        self.assertEqual(MessageType.PROMPT.value, "prompt")
        self.assertEqual(MessageType.COMMAND.value, "command")
    
    def test_message_type_from_string(self):
        """Test MessageType.from_string method."""
        self.assertEqual(
            MessageType.from_string("prompt"),
            MessageType.PROMPT
        )
        self.assertEqual(
            MessageType.from_string("unknown"),
            MessageType.MESSAGE  # Default
        )
    
    def test_session_metadata(self):
        """Test SessionMetadata class."""
        from skyhook.protocol.message_formats import SessionMetadata
        
        metadata = SessionMetadata(
            source_repo="timerloggedout-spec/termux-monorepo",
            source_branch="master-staging",
            target_branch="feature/skyhook",
            session_type=SessionType.INTERACTIVE,
            priority="high",
            labels=["skyhook", "integration"],
        )
        
        data = metadata.to_dict()
        self.assertEqual(data["source_repo"], "timerloggedout-spec/termux-monorepo")
        self.assertEqual(data["source_branch"], "master-staging")
        self.assertEqual(data["session_type"], "INTERACTIVE")
        
        # Test from_dict
        metadata2 = SessionMetadata.from_dict(data)
        self.assertEqual(metadata2.source_repo, metadata.source_repo)
        self.assertEqual(metadata2.session_type, SessionType.INTERACTIVE)
    
    def test_jules_request(self):
        """Test JulesRequest class."""
        from skyhook.protocol.message_formats import SessionMetadata
        
        request = JulesRequest(
            session_id="sess_123",
            message_type=MessageType.PROMPT,
            content="Implement SKYHOOK integration",
            metadata=SessionMetadata(source_repo="test/repo"),
        )
        
        data = request.to_dict()
        self.assertEqual(data["session_id"], "sess_123")
        self.assertEqual(data["message_type"], "prompt")
        self.assertEqual(data["content"], "Implement SKYHOOK integration")
        
        # Test JSON serialization
        json_str = request.to_json()
        self.assertIsInstance(json_str, str)
        
        # Test from_json
        request2 = JulesRequest.from_json(json_str)
        self.assertEqual(request2.session_id, request.session_id)
        self.assertEqual(request2.message_type, MessageType.PROMPT)
    
    def test_session_activity(self):
        """Test SessionActivity class."""
        activity = SessionActivity(
            activity_id="act_123",
            activity_type="plan",
            content="Create integration layer",
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
        
        data = activity.to_dict()
        self.assertEqual(data["activity_id"], "act_123")
        self.assertEqual(data["activity_type"], "plan")
        
        # Test from_dict
        activity2 = SessionActivity.from_dict(data)
        self.assertEqual(activity2.activity_id, activity.activity_id)
    
    def test_session_artifact(self):
        """Test SessionArtifact class."""
        artifact = SessionArtifact(
            artifact_id="art_123",
            artifact_type="patch",
            name="integration.patch",
            content="diff --git a/...",
            size_bytes=1024,
        )
        
        data = artifact.to_dict()
        self.assertEqual(data["artifact_id"], "art_123")
        self.assertEqual(data["artifact_type"], "patch")
        
        # Test from_dict
        artifact2 = SessionArtifact.from_dict(data)
        self.assertEqual(artifact2.artifact_id, artifact.artifact_id)
    
    def test_jules_response(self):
        """Test JulesResponse class."""
        response = JulesResponse(
            session_id="sess_123",
            state=SessionState.COMPLETED,
            activities=[
                SessionActivity(
                    activity_id="act_1",
                    activity_type="plan",
                    content="Plan created",
                    timestamp=datetime.utcnow().isoformat() + "Z",
                ),
            ],
            artifacts=[
                SessionArtifact(
                    artifact_id="art_1",
                    artifact_type="patch",
                    name="changes.patch",
                ),
            ],
        )
        
        data = response.to_dict()
        self.assertEqual(data["session_id"], "sess_123")
        self.assertEqual(data["state"], "COMPLETED")
        self.assertEqual(len(data["activities"]), 1)
        self.assertEqual(len(data["artifacts"]), 1)
        
        # Test properties
        self.assertTrue(response.is_terminal)
        self.assertFalse(response.is_waiting)
        self.assertFalse(response.has_error)
        self.assertTrue(response.has_artifacts)
        
        # Test get_patches
        patches = response.get_patches()
        self.assertEqual(len(patches), 1)
        
        # Test JSON serialization
        json_str = response.to_json()
        self.assertIsInstance(json_str, str)
        
        # Test from_json
        response2 = JulesResponse.from_json(json_str)
        self.assertEqual(response2.session_id, response.session_id)
        self.assertEqual(response2.state, SessionState.COMPLETED)


class TestErrorCodes(unittest.TestCase):
    """Test error code classes."""
    
    def test_error_code_enum(self):
        """Test ErrorCode enum."""
        self.assertEqual(ErrorCode.AUTH_MISSING_API_KEY.value, "AUTH_001")
        self.assertEqual(ErrorCode.CONFIG_MISSING_REPO.value, "CONFIG_001")
    
    def test_error_code_category(self):
        """Test ErrorCode.category property."""
        self.assertEqual(ErrorCode.AUTH_MISSING_API_KEY.category, "AUTH")
        self.assertEqual(ErrorCode.CONFIG_MISSING_REPO.category, "CONFIG")
    
    def test_error_type_enum(self):
        """Test ErrorType enum."""
        self.assertEqual(ErrorType.TRANSIENT.value, "transient")
        self.assertEqual(ErrorType.CONFIGURATION.value, "configuration")
    
    def test_skyhook_error(self):
        """Test SkyhookError class."""
        error = SkyhookError(
            code=ErrorCode.AUTH_MISSING_API_KEY,
            message="JULES_API_KEY not set",
        )
        
        self.assertEqual(error.code, ErrorCode.AUTH_MISSING_API_KEY)
        self.assertEqual(error.message, "JULES_API_KEY not set")
        self.assertEqual(error.error_type, ErrorType.AUTHENTICATION)
        self.assertFalse(error.is_retryable)
        self.assertTrue(error.requires_user_action)
        
        # Test to_dict
        data = error.to_dict()
        self.assertEqual(data["code"], "AUTH_001")
        self.assertEqual(data["message"], "JULES_API_KEY not set")
        self.assertEqual(data["type"], "authentication")
    
    def test_transient_error(self):
        """Test TransientError class."""
        error = TransientError(
            code=ErrorCode.NETWORK_CONNECTION_FAILED,
            message="Connection timeout",
            retry_after=10.0,
        )
        
        self.assertTrue(error.is_retryable)
        self.assertFalse(error.requires_user_action)
        self.assertEqual(error.retry_after, 10.0)
    
    def test_configuration_error(self):
        """Test ConfigurationError class."""
        error = ConfigurationError(
            code=ErrorCode.CONFIG_MISSING_REPO,
            message="Repository not configured",
        )
        
        self.assertFalse(error.is_retryable)
        self.assertTrue(error.requires_user_action)
    
    def test_authentication_error(self):
        """Test AuthenticationError class."""
        error = AuthenticationError(
            code=ErrorCode.AUTH_INVALID_API_KEY,
            message="Invalid API key",
        )
        
        self.assertFalse(error.is_retryable)
        self.assertTrue(error.requires_user_action)
    
    def test_rate_limit_error(self):
        """Test RateLimitError class."""
        error = RateLimitError(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message="Rate limit exceeded",
            retry_after=60.0,
        )
        
        self.assertTrue(error.is_retryable)
        self.assertFalse(error.requires_user_action)
    
    def test_resource_error(self):
        """Test ResourceError class."""
        error = ResourceError(
            code=ErrorCode.RESOURCE_OUT_OF_MEMORY,
            message="Out of memory",
        )
        
        self.assertFalse(error.is_retryable)
        self.assertFalse(error.requires_user_action)
    
    def test_create_error_from_response(self):
        """Test create_error_from_response function."""
        # Test jules-dispatch-cli style
        response = {
            "error": {
                "code": "AUTH_002",
                "message": "Invalid API key",
            }
        }
        error = create_error_from_response(response)
        self.assertEqual(error.code, ErrorCode.AUTH_INVALID_API_KEY)
        self.assertEqual(error.message, "Invalid API key")
        
        # Test HTTP error style
        response = {
            "status": 401,
            "message": "Unauthorized",
        }
        error = create_error_from_response(response)
        self.assertEqual(error.code, ErrorCode.AUTH_INVALID_API_KEY)
        
        # Test unknown format
        response = {"unknown": "error"}
        error = create_error_from_response(response)
        self.assertEqual(error.code, ErrorCode.UNKNOWN_ERROR)


if __name__ == "__main__":
    unittest.main()
