"""
ARUS
Verifier - Fase 7

Comprueba que una respuesta de un agente:
1. existe,
2. tiene un resultado válido,
3. no contiene errores,
4. puede marcarse como verificada.

No ejecuta herramientas por segunda vez.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VerificationResult:
    verified: bool
    reason: str = ""
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class Verifier:
    """
    Verificador básico de respuestas de agentes.

    Fase 7:
    - valida AgentResponse
    - detecta respuestas fallidas
    - detecta respuestas vacías
    - conserva información de diagnóstico
    """

    def verify(self, response) -> VerificationResult:
        errors = []

        if response is None:
            errors.append("La respuesta es None.")

            return VerificationResult(
                verified=False,
                reason="Respuesta inexistente.",
                errors=errors,
            )

        # success
        if not getattr(response, "success", False):
            existing_errors = getattr(response, "errors", [])

            if existing_errors:
                errors.extend(
                    str(error)
                    for error in existing_errors
                )

            if not errors:
                errors.append(
                    "El agente indicó que la operación falló."
                )

        # answer
        answer = getattr(response, "answer", "")

        if answer is None:
            errors.append(
                "La respuesta no contiene answer."
            )
        elif not isinstance(answer, str):
            errors.append(
                "answer no es de tipo str."
            )
        elif not answer.strip():
            errors.append(
                "La respuesta está vacía."
            )

        if errors:
            return VerificationResult(
                verified=False,
                reason="La respuesta no pasó la verificación.",
                errors=errors,
                metadata={
                    "response_type": type(response).__name__,
                },
            )

        return VerificationResult(
            verified=True,
            reason="Respuesta válida.",
            metadata={
                "response_type": type(response).__name__,
                "answer_length": len(answer),
            },
        )
