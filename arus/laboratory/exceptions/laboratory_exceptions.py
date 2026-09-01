"""
ARUS
Virtual Laboratory
Exceptions
"""


class LaboratoryError(Exception):
    """
    Excepción base del laboratorio.
    """


class LaboratoryAlreadyExistsError(LaboratoryError):
    """
    El laboratorio ya existe.
    """


class LaboratoryNotFoundError(LaboratoryError):
    """
    Laboratorio no encontrado.
    """


class LaboratoryAlreadyRunningError(LaboratoryError):
    """
    El laboratorio ya está en ejecución.
    """


class LaboratoryNotRunningError(LaboratoryError):
    """
    El laboratorio no está en ejecución.
    """


class InvalidLaboratoryStateError(LaboratoryError):
    """
    Estado inválido del laboratorio.
    """


class WorkspaceError(LaboratoryError):
    """
    Error relacionado con un Workspace.
    """


class WorkspaceAlreadyExistsError(WorkspaceError):
    """
    El Workspace ya existe.
    """


class WorkspaceNotFoundError(WorkspaceError):
    """
    Workspace no encontrado.
    """


class ExperimentError(LaboratoryError):
    """
    Error relacionado con un experimento.
    """


class ExperimentAlreadyExistsError(ExperimentError):
    """
    El experimento ya existe.
    """


class ExperimentNotFoundError(ExperimentError):
    """
    Experimento no encontrado.
    """


class ConfigurationError(LaboratoryError):
    """
    Error de configuración.
    """
