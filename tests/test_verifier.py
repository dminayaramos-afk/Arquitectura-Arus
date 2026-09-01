"""
ARUS - Fase 7
Tests del Verifier
"""

from agents.agent_response import AgentResponse
from verification.verifier import Verifier


def test_valid_response():
    verifier = Verifier()

    response = AgentResponse(
        True,
        "5",
    )

    result = verifier.verify(response)

    assert result.verified is True
    assert result.errors == []


def test_failed_response():
    verifier = Verifier()

    response = AgentResponse(
        False,
        "",
        errors=["fallo de herramienta"],
    )

    result = verifier.verify(response)

    assert result.verified is False
    assert "fallo de herramienta" in result.errors


def test_empty_response():
    verifier = Verifier()

    response = AgentResponse(
        True,
        "",
    )

    result = verifier.verify(response)

    assert result.verified is False


def test_none_response():
    verifier = Verifier()

    result = verifier.verify(None)

    assert result.verified is False
