import platform
import subprocess
from importlib.metadata import version
from pathlib import Path

def collect_code_info(project_root: Path) -> Path:
    """Consulta el commit y los cambios del repositorio indicado."""

    commit_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=True,
    )

    status_result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=True,
    )

    return {
        "commit": commit_result.stdout.strip(),
        "working_tree_dirty": bool(status_result.stdout.strip()),
    }

def collect_environment_info() -> dict:
    """Recoge una descripcion minima del entorno Python activo."""

    return{
        "python_version": platform.python_version(),
        "dependencies": {
            "numpy": version("numpy"),
            "pandas": version("pandas")
        },
    }