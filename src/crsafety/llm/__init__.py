"""Kaggle LLM stack (H3): model registry and pins, call cache, cached client, vLLM servers.

See kaggle/README.md for the Kaggle workflow and configs/llm/ for the models.
"""

from .cache import CallCache, call_key
from .client import Client, ServerError
from .models import ModelSpec, NotPinned, candidate_spec, load_registry, resolve

__all__ = ["CallCache", "call_key", "Client", "ServerError", "ModelSpec", "NotPinned",
           "candidate_spec", "load_registry", "resolve"]
