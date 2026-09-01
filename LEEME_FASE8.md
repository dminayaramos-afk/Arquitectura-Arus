# ARUS MARK 7 — FASE 8: RAG + documentos + proyectos

## Como instalar
Añade/sustituye (mismas rutas):

    rag/__init__.py            (nuevo)
    rag/document_parser.py     (nuevo)
    rag/chunker.py              (nuevo)
    rag/embeddings.py           (nuevo)
    rag/vector_store.py         (nuevo)
    rag/retriever.py            (nuevo)
    rag/project_scanner.py      (nuevo)
    rag/rag_manager.py          (nuevo)
    database/rag_chunk_repository.py (nuevo)
    brain/brain.py              (modificado: expone self.rag)

No se toco `arus/interface/*`.

## Auditoria previa
Se busco "rag"/"embedding"/"vector"/"chunk" en todo el proyecto antes
de escribir nada: no habia nada real (solo comentarios propios de la
Fase 5 que ya apuntaban aqui, y un falso positivo de CSS
`QProgressBar::chunk`). Fase 8 es infraestructura nueva.

## Decision de diseño importante: embeddings ligeros, no un modelo
En vez de descargar un modelo de embeddings (que necesitaria
internet, espacio en disco y mas RAM), se implemento un embedding por
"hashing trick": cada palabra cae en una posicion fija de un vector
de 256 dimensiones segun su hash, se cuenta su frecuencia y se
normaliza. Es determinista, funciona sin conexion y es liviano —
coherente con la filosofia de adaptacion a hardware limitado que pide
el prompt maestro en los puntos 67-95 (que todavia no existen como
CapabilityManager, pero el criterio ya se puede aplicar aqui).

**Limitacion honesta:** esto es busqueda por coincidencia de
palabras, NO comprension semantica. "Como funciona la voz de ARUS"
encuentra bien un documento que literalmente habla de voz/TTS, pero
una consulta con sinonimos o parafraseada puede no encontrar el
fragmento correcto (lo comprobe: una consulta parafraseada sobre
"similitud entre vectores" devolvio el archivo equivocado; con
terminos literales del propio codigo, funciono bien). Si mas adelante
hay hardware/API para un modelo de embeddings real, `Embeddings` se
puede sustituir sin tocar `VectorStore` ni `Retriever`.

## Pipeline implementado (punto 23)
    Documents -> Parser -> Chunking -> Embeddings -> Vector Store -> Retriever

- `DocumentParser`: lee texto/Markdown/codigo (extensiones
  explicitas). PDF/DOCX quedan fuera — necesitarian pypdf/python-docx,
  no confirmadas en el proyecto; no se finge soporte.
- `Chunker`: fragmentos de ~1200 caracteres con solapamiento, para no
  cortar ideas a la mitad.
- `Embeddings`: ver arriba.
- `VectorStore`: persiste en SQLite (tabla `rag_chunks`, con
  `project` para separar distintos proyectos indexados) y busca por
  similitud de coseno en Python.
- `Retriever`: `retrieve()`/`retrieve_as_text()` — da el contexto
  relevante en vez de meter el documento entero (punto 23).

## Proyectos (punto 24 y 55, "aprende este proyecto")
`ProjectScanner` recorre un directorio ignorando `__pycache__`, `.git`,
`venv`, `node_modules`, etc., y `RAGManager.index_project()` hace
scan -> leer -> indexar -> devolver un resumen de HECHOS (archivos
encontrados/indexados, fragmentos, omitidos con motivo). No genera un
resumen en lenguaje natural del proyecto — eso necesita al modelo
razonando sobre lo indexado, que es integracion con Brain (ver
siguiente seccion), no esta fase.

## Por que NO se conecto a Brain.think() automaticamente
`Brain` ahora expone `self.rag` (funcional, probado), pero
deliberadamente NO se engancha a la conversacion normal. Decidir
CUANDO usar RAG (¿en cada mensaje? ¿solo si se detecta cierta
intencion tipo "explica el proyecto"?) es una decision de producto
que tocaria el flujo ya probado de las Fases 2-7 y podia introducir
una regresion silenciosa. Se deja listo para conectarlo explicitamente
cuando tu digas como quieres que se dispare.

## Probado
1. `Chunker` fragmenta con el limite de tamaño esperado.
2. `Embeddings` es determinista (mismo texto -> mismo vector) y
   distingue textos relacionados de no relacionados.
3. Indexar 2 documentos reales y consultar: encuentra el documento
   correcto, no el otro.
4. Reindexar un archivo reemplaza sus fragmentos viejos (no se
   acumulan versiones antiguas).
5. Un archivo con extension no soportada (.png) se rechaza con un
   error claro, no se intenta leer a ciegas.
6. Escaneo real de la propia carpeta `rag/` de esta entrega: 8
   archivos, 15 fragmentos indexados; consultas con terminos
   literales encuentran el archivo correcto.
7. `Brain` expone `self.rag` funcional y no rompe nada: chat normal,
   memoria de nombre y persistencia de conversacion (Fases 2, 3, 5)
   siguen funcionando igual.
8. Interfaz: `main_window.py`, `controller.py`, `core_visual.py`
   identicos byte a byte.
9. Sintaxis de todo el proyecto (`py_compile`): OK.

## FASE 8 — RESULTADO

Archivos creados:
- rag/__init__.py, rag/document_parser.py, rag/chunker.py,
  rag/embeddings.py, rag/vector_store.py, rag/retriever.py,
  rag/project_scanner.py, rag/rag_manager.py
- database/rag_chunk_repository.py

Archivos modificados:
- brain/brain.py (expone self.rag; NO conectado al flujo de think())

Archivos NO modificados:
- arus/interface/* (identico byte a byte)
- resto del proyecto

Pruebas: 9 casos reales, todos OK (ver arriba).
Interfaz visual: sin cambios.
Arranque completo con PySide6/Ollama reales: NO VERIFICADO en este
entorno (paquetes no instalados aqui) — confirmalo en tu maquina.

Pendiente para siguientes fases: decidir y conectar cuándo Brain usa
RAG automaticamente (posible sub-tarea de una fase futura o de la
Fase 9/10 cuando haya mas contexto de codigo/Git que indexar); Fase 9
(Git/GitHub), Fase 10 (asistente de programacion), y de ahi en
adelante voz, vision, tareas autonomas, seguridad, plugins y
evaluacion (Fases 11-16). Sigue pendiente tambien la decision sobre
la arquitectura de agentes duplicada auditada en la Fase 6.
