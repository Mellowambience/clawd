"""TDD tests for MIST provenance — honest self-knowledge tags."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from gateway.provenance import tag, tag_self


def test_local_model_tagged_local():
    out = tag("hello", source="ollama", model="mistral")
    assert out["provenance"] == "local:ollama/mistral"
    assert out["text"] == "hello"


def test_cloud_model_tagged_cloud():
    out = tag("think", source="gemini", model="flash")
    assert out["provenance"].startswith("cloud:")


def test_retrieved_document_labeled():
    out = tag("fact", source="memory", model="sqlite", doc="user_profile")
    assert "doc:user_profile" in out["provenance"]


def test_self_knowledge_honest():
    sk = tag_self(name="MIST", state="awake", model_layer="hybrid")
    assert sk["provenance"] == "self:code-asserted"
    assert sk["self"]["lives_in_gateway_cloud"] is True
