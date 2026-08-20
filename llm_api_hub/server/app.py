"""Local OpenAI-compatible gateway for the Termux monorepo ADE.

The hub deliberately keeps provider credentials and wrapper session state outside
of git.  It exposes one stable contract while routing to the existing
``multi-ai-cli`` wrappers or explicitly configured OpenAI-compatible upstreams.

Run from the repository root with::

    uvicorn llm-api-hub.server.app:app --host 127.0.0.1 --port 8787

Because ``llm-api-hub`` contains a hyphen, the supported executable form is also
available from this directory::

    cd llm-api-hub/server && uvicorn app:app --host 127.0.0.1 --port 8787
"""
# Keep annotations eagerly resolved: this module is also loaded directly by
# Termux launchers, not only through a package import.
import hmac
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field


REPO_ROOT = Path(__file__).resolve().parents[2]
MULTI_AI_CLI = REPO_ROOT / "multi-ai-cli"

# Ensure multi-ai-cli is in path for core imports
if str(MULTI_AI_CLI) not in sys.path:
    sys.path.insert(0, str(MULTI_AI_CLI))

try:
    from core import provider_checklist, provider_registry
except ImportError:
    provider_checklist = None
    provider_registry = None
DEFAULT_HOST = os.environ.get("LLM_API_HUB_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("LLM_API_HUB_PORT", "8787"))
REQUEST_TIMEOUT = float(os.environ.get("LLM_API_HUB_TIMEOUT", "120"))


class HubError(Exception):
    """An expected request or provider failure with an HTTP-compatible status."""

    def __init__(self, status_code: int, message: str, *, code: str = "hub_error") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.code = code


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    role: str
    content: Any = ""
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str = Field(min_length=1)
    messages: List[ChatMessage] = Field(min_length=1)
    temperature: Optional[float] = None
    max_tokens: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = None
    stop: Optional[Any] = None
    stream: bool = False
    # Optional hub extension. It is ignored by upstream providers and can be
    # used by callers that want multi-turn wrapper session persistence.
    session_id: Optional[str] = None


class HubRuntime:
    """Lazy provider runtime so health/models endpoints do not require tokens."""

    def __init__(self) -> None:
        self._dispatcher: Any = None

    def _get_dispatcher(self) -> Any:
        if self._dispatcher is None:
            if not MULTI_AI_CLI.exists():
                raise HubError(500, "multi-ai-cli directory is missing", code="runtime_missing")
            sys.path.insert(0, str(MULTI_AI_CLI))
            try:
                from core.chat_dispatcher import ChatDispatcher  # type: ignore
                from core.session_manager import SessionManager  # type: ignore

                self._dispatcher = ChatDispatcher(SessionManager())
            except Exception as exc:  # imports are intentionally lazy
                raise HubError(
                    503,
                    f"multi-ai-cli runtime is unavailable: {exc}",
                    code="runtime_unavailable",
                ) from exc
        return self._dispatcher

    def complete_wrapper(self, provider: str, request: ChatCompletionRequest) -> str:
        dispatcher = self._get_dispatcher()
        prompt = messages_to_prompt(request.messages)
        try:
            if request.session_id:
                return str(dispatcher.send(provider, prompt, request.session_id))
            backend = dispatcher.get_backend(provider)
            return str(backend.send_message(prompt, []))
        except HubError:
            raise
        except Exception as exc:
            raise HubError(
                503,
                f"wrapper backend '{provider}' failed: {exc}",
                code="provider_unavailable",
            ) from exc

    def complete_upstream(self, provider: str, request: ChatCompletionRequest) -> Dict[str, Any]:
        if provider == "anthropic":
            return self._complete_anthropic(request)

        if provider == "openrouter":
            base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            api_key = os.environ.get("OPENROUTER_API_KEY")
            extra_headers = {
                "HTTP-Referer": os.environ.get("OPENROUTER_HTTP_REFERER", "http://127.0.0.1"),
                "X-Title": os.environ.get("OPENROUTER_X_TITLE", "termux-monorepo llm-api-hub"),
            }
        elif provider == "openai":
            base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            api_key = os.environ.get("OPENAI_API_KEY")
            extra_headers = {}
        elif provider == "xai":
            base_url = os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1")
            api_key = os.environ.get("XAI_API_KEY")
            extra_headers = {}
        else:
            raise HubError(400, f"unsupported upstream provider '{provider}'", code="unsupported_provider")

        if not api_key:
            raise HubError(
                503,
                f"{provider} is not configured; set {provider.upper()}_API_KEY",
                code="provider_unconfigured",
            )

        model = request.model.split("/", 1)[1] if "/" in request.model else request.model
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [message_to_dict(message) for message in request.messages],
            "stream": False,
        }
        for key in ("temperature", "max_tokens", "top_p", "stop"):
            value = getattr(request, key)
            if value is not None:
                payload[key] = value

        response = http_json(
            f"{base_url.rstrip('/')}/chat/completions",
            payload,
            headers={"Authorization": f"Bearer {api_key}", **extra_headers},
            timeout=REQUEST_TIMEOUT,
        )
        return normalize_openai_response(response, request.model)

    def _complete_anthropic(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise HubError(503, "anthropic is not configured; set ANTHROPIC_API_KEY", code="provider_unconfigured")

        model = request.model.split("/", 1)[1] if "/" in request.model else request.model
        system_parts = [content_to_text(message.content) for message in request.messages if message.role == "system"]
        messages = [
            {"role": message.role, "content": message.content}
            for message in request.messages
            if message.role in {"user", "assistant"}
        ]
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or 1024,
        }
        if system_parts:
            payload["system"] = "\n\n".join(part for part in system_parts if part)
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        response = http_json(
            os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com") .rstrip("/") + "/v1/messages",
            payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            timeout=REQUEST_TIMEOUT,
        )
        text = "\n".join(
            block.get("text", "")
            for block in response.get("content", [])
            if isinstance(block, dict) and block.get("type") == "text"
        )
        return completion_response(request.model, text, response.get("usage"))


runtime = HubRuntime()
app = FastAPI(title="llm-api-hub", version="1.0.0", docs_url="/docs", redoc_url=None)


def content_to_text(content: Any) -> str:
    """Convert OpenAI text or multimodal content parts into a safe prompt string."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") in {"text", "input_text"}:
                    parts.append(str(item.get("text", "")))
                elif item.get("type") in {"image_url", "input_image"}:
                    parts.append("[image content omitted from wrapper prompt]")
                else:
                    parts.append(json.dumps(item, sort_keys=True))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part)
    return str(content)


def message_to_dict(message: ChatMessage) -> Dict[str, Any]:
    result: Dict[str, Any] = {"role": message.role, "content": message.content}
    if message.name:
        result["name"] = message.name
    return result


def messages_to_prompt(messages: Iterable[ChatMessage]) -> str:
    """Render a multi-turn OpenAI conversation for legacy wrapper backends."""
    rendered: List[str] = []
    for message in messages:
        text = content_to_text(message.content)
        if not text:
            continue
        rendered.append(f"[{message.role}]\n{text}")
    if not rendered:
        raise HubError(400, "messages must contain text content", code="invalid_messages")
    return "\n\n".join(rendered) + "\n\n[assistant]"


def http_json(url: str, payload: Dict[str, Any], *, headers: Dict[str, str], timeout: float) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = UrlRequest(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json", **headers},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            decoded = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:4000]
        raise HubError(502, f"upstream returned HTTP {exc.code}: {detail}", code="upstream_error") from exc
    except (URLError, TimeoutError) as exc:
        raise HubError(502, f"upstream is unreachable: {exc}", code="upstream_unreachable") from exc
    except json.JSONDecodeError as exc:
        raise HubError(502, "upstream returned invalid JSON", code="upstream_invalid_json") from exc
    if not isinstance(decoded, dict):
        raise HubError(502, "upstream returned a non-object response", code="upstream_invalid_response")
    return decoded


def normalize_openai_response(response: Dict[str, Any], requested_model: str) -> Dict[str, Any]:
    choices = response.get("choices")
    if not isinstance(choices, list):
        raise HubError(502, "upstream response has no choices", code="upstream_invalid_response")
    response = dict(response)
    response.setdefault("id", f"chatcmpl-{uuid.uuid4().hex}")
    response.setdefault("object", "chat.completion")
    response.setdefault("created", int(time.time()))
    response["model"] = requested_model
    return response


def completion_response(model: str, text: str, usage: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response: Dict[str, Any] = {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
    }
    if usage is not None:
        response["usage"] = usage
    return response


def validate_auth(request: Request) -> None:
    expected = os.environ.get("LLM_API_HUB_KEY")
    if not expected:
        return
    authorization = request.headers.get("authorization", "")
    supplied = authorization.removeprefix("Bearer ").strip()
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise HubError(401, "invalid or missing hub authorization", code="unauthorized")


def configured_models() -> List[str]:
    models = [
        "wrapper/deepseek", "wrapper/mistral", "wrapper/grok", 
        "wrapper/claude", "wrapper/gemini", "wrapper/colab",
        "wrapper/perplexity", "wrapper/kimi"
    ]
    if os.environ.get("OPENROUTER_API_KEY"):
        models.append("openrouter/<model>")
    if os.environ.get("OPENAI_API_KEY"):
        models.append("openai/<model>")
    if os.environ.get("ANTHROPIC_API_KEY"):
        models.append("anthropic/<model>")
    if os.environ.get("XAI_API_KEY"):
        models.append("xai/<model>")
    return models


@app.exception_handler(HubError)
def hub_error_handler(_: Request, exc: HubError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"message": exc.message, "type": exc.code, "code": exc.code}},
    )


@app.get("/")
def root() -> Dict[str, Any]:
    return {"name": "llm-api-hub", "version": app.version, "endpoint": "/v1/chat/completions"}


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "llm-api-hub",
        "host": DEFAULT_HOST,
        "port": DEFAULT_PORT,
        "configured_upstreams": {
            "openrouter": bool(os.environ.get("OPENROUTER_API_KEY")),
            "openai": bool(os.environ.get("OPENAI_API_KEY")),
            "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        },
    }


@app.get("/v1/providers")
def list_providers(request: Request) -> List[Dict[str, Any]]:
    validate_auth(request)
    if not provider_checklist:
        raise HubError(501, "provider checklist is not available", code="not_implemented")
    return provider_checklist.public_view(provider_checklist.load_state())


class TransitionRequest(BaseModel):
    state: str
    account: Optional[str] = None
    reason: Optional[str] = None


@app.post("/v1/providers/{provider_id}/transition")
def transition_provider(provider_id: str, request: TransitionRequest, raw_request: Request) -> Dict[str, Any]:
    validate_auth(raw_request)
    if not provider_checklist:
        raise HubError(501, "provider checklist is not available", code="not_implemented")
    
    state = provider_checklist.load_state()
    try:
        updated = provider_checklist.transition(
            state, 
            provider_id, 
            request.state, 
            account=request.account, 
            reason=request.reason
        )
        provider_checklist.save_state(updated)
        return {"status": "success", "provider_id": provider_id, "state": request.state}
    except ValueError as exc:
        raise HubError(400, str(exc), code="invalid_transition")


@app.get("/v1/models")
def models(request: Request) -> Dict[str, Any]:
    validate_auth(request)
    now = int(time.time())
    return {
        "object": "list",
        "data": [
            {"id": model, "object": "model", "created": now, "owned_by": "termux-monorepo"}
            for model in configured_models()
        ],
    }


@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest, raw_request: Request) -> Any:
    validate_auth(raw_request)
    return handle_completion(request)

@app.post("/v1/messages")
def anthropic_messages(request: ChatCompletionRequest, raw_request: Request) -> Any:
    """Anthropic-native Messages API compatibility."""
    validate_auth(raw_request)
    response = handle_completion(request)
    if isinstance(response, dict) and "choices" in response:
        content = response["choices"][0]["message"]["content"]
        return {
            "id": response["id"],
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content}],
            "model": response["model"],
            "usage": response.get("usage", {"input_tokens": 0, "output_tokens": 0})
        }
    return response

@app.post("/v1/models/{model_name}:generateContent")
def google_generate_content(model_name: str, request_data: Dict[str, Any], raw_request: Request) -> Any:
    """Google Gemini-native generateContent API compatibility."""
    validate_auth(raw_request)
    messages = []
    for part in request_data.get("contents", []):
        role = "user" if part.get("role") == "user" else "assistant"
        content = ""
        for p in part.get("parts", []):
            if "text" in p:
                content += p["text"]
        messages.append(ChatMessage(role=role, content=content))
    
    hub_request = ChatCompletionRequest(model=model_name, messages=messages)
    response = handle_completion(hub_request)
    
    if isinstance(response, dict) and "choices" in response:
        content = response["choices"][0]["message"]["content"]
        return {
            "candidates": [{
                "content": {"parts": [{"text": content}], "role": "model"},
                "finishReason": "STOP"
            }],
            "usageMetadata": {
                "promptTokenCount": response.get("usage", {}).get("prompt_tokens", 0),
                "candidatesTokenCount": response.get("usage", {}).get("completion_tokens", 0)
            }
        }
    return response

def handle_completion(request: ChatCompletionRequest) -> Any:
    model = request.model.strip()
    if model.startswith("wrapper/"):
        provider = model.split("/", 1)[1]
        if provider not in {"deepseek", "mistral", "grok", "claude", "gemini", "colab", "perplexity", "kimi"}:
            raise HubError(400, f"unknown wrapper model '{model}'", code="unknown_model")
        text = runtime.complete_wrapper(provider, request)
        response = completion_response(model, text)
    elif model.startswith("openrouter/"):
        response = runtime.complete_upstream("openrouter", request)
    elif model.startswith("openai/"):
        response = runtime.complete_upstream("openai", request)
    elif model.startswith("anthropic/"):
        response = runtime.complete_upstream("anthropic", request)
    elif model.startswith("xai/"):
        response = runtime.complete_upstream("xai", request)
    elif "/" not in model and os.environ.get("OPENROUTER_API_KEY"):
        response = runtime.complete_upstream("openrouter", request)
    else:
        raise HubError(
            400,
            "model must use wrapper/<name>, openrouter/<model>, openai/<model>, or anthropic/<model>",
            code="unknown_model",
        )

    if not request.stream:
        return response
    return StreamingResponse(sse_events(response), media_type="text/event-stream")


def sse_events(response: Dict[str, Any]) -> Iterator[str]:
    """Emit a standards-compatible, single-batch SSE response for sync backends."""
    choice = (response.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    text = message.get("content") or ""
    base = {
        "id": response.get("id"),
        "object": "chat.completion.chunk",
        "created": response.get("created", int(time.time())),
        "model": response.get("model"),
    }
    yield f"data: {json.dumps({**base, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"
    if text:
        yield f"data: {json.dumps({**base, 'choices': [{'index': 0, 'delta': {'content': text}, 'finish_reason': None}]})}\n\n"
    yield f"data: {json.dumps({**base, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
    yield "data: [DONE]\n\n"


__all__ = ["app", "chat_completions", "completion_response", "messages_to_prompt"]
