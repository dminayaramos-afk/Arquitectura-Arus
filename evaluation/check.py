"""
ARUS
Evaluation Check (Fase 16)

Infraestructura mínima: cada prueba se ejecuta de forma aislada. Si
una prueba lanza una excepción, no tumba a las demás (punto 45: no
mostrar tracebacks técnicos) -- se registra como fallo con el motivo,
igual que el resto de esta fase.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class CheckResult:

    name: str
    category: str
    passed: bool
    detail: str = ""
    skipped: bool = False
    duration_ms: float = 0.0


@dataclass
class Suite:

    results: list = field(default_factory=list)

    def run(self, category: str, name: str, fn: Callable[[], Optional[str]]):
        """
        `fn` debe devolver None (o no lanzar) si la prueba pasa, o
        lanzar una excepción / devolver un string con el motivo si
        falla. Devolver la cadena literal 'SKIP:...' marca la prueba
        como no verificable en este entorno (no como fallo real).
        """

        inicio = time.time()

        try:

            resultado = fn()

            duracion = (time.time() - inicio) * 1000

            if isinstance(resultado, str) and resultado.startswith("SKIP:"):

                self.results.append(CheckResult(
                    name, category, passed=True, skipped=True,
                    detail=resultado[5:].strip(), duration_ms=duracion,
                ))

            elif resultado:

                self.results.append(CheckResult(
                    name, category, passed=False,
                    detail=str(resultado), duration_ms=duracion,
                ))

            else:

                self.results.append(CheckResult(
                    name, category, passed=True, duration_ms=duracion,
                ))

        except Exception as e:

            duracion = (time.time() - inicio) * 1000

            self.results.append(CheckResult(
                name, category, passed=False,
                detail=f"{type(e).__name__}: {e}", duration_ms=duracion,
            ))

    def report(self) -> str:

        categorias = {}

        for r in self.results:
            categorias.setdefault(r.category, []).append(r)

        lineas = ["=" * 60, "ARUS MARK 7 -- INFORME DE EVALUACIÓN", "=" * 60, ""]

        total_ok = total_fail = total_skip = 0

        for categoria, items in categorias.items():

            lineas.append(f"[{categoria}]")

            for r in items:

                if r.skipped:
                    marca = "○ SKIP"
                    total_skip += 1
                elif r.passed:
                    marca = "✓ OK  "
                    total_ok += 1
                else:
                    marca = "✗ FAIL"
                    total_fail += 1

                detalle = f" -- {r.detail}" if r.detail else ""

                lineas.append(f"  {marca}  {r.name}{detalle}")

            lineas.append("")

        lineas.append("-" * 60)
        lineas.append(f"OK: {total_ok}   FALLOS: {total_fail}   NO VERIFICABLE: {total_skip}")
        lineas.append("-" * 60)

        return "\n".join(lineas)

    def all_passed(self) -> bool:

        return all(r.passed for r in self.results)
