"""
ARUS
Context Retriever

Recupera información relevante
para construir el contexto.
"""

from __future__ import annotations


class ContextRetriever:


    def __init__(
        self,
        memory_manager=None,
    ):

        self.memory = memory_manager


    def retrieve(
        self,
        query: str,
    ) -> list[dict]:
        """
        Recupera recuerdos relacionados.
        """

        results = []


        if self.memory is None:

            return results


        memories = self.memory.long.all()


        for key, value in memories.items():

            if query.lower() in key.lower():

                results.append(
                    {
                        "role": "memory",
                        "content": value,
                    }
                )


        return results
