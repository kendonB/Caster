# pylint: disable=import-error,no-name-in-module

"""
Minimal PySide2/PySide6 compatibility helpers.
"""


try:
    from PySide2 import QtCore, QtGui, QtWidgets  # type: ignore
    QT_API = "PySide2"
except ImportError as pyside2_err:  # pragma: no cover
    try:
        from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore
        QT_API = "PySide6"
    except ImportError as pyside6_err:  # pragma: no cover
        raise ImportError(
            "Unable to import Qt bindings (PySide2/PySide6). "
            "Qt is required for HUD/settings/HMC UI features. "
            "On Windows x64, rerun the Caster installer or install with: "
            "uv pip install --python .venv\\Scripts\\python.exe \"PySide6>=6.6\""
        ) from pyside6_err


def qt_attr(root, *paths):
    """
    Return the first attribute path that exists on `root`.

    `paths` should be tuples of attribute names, e.g. ("Qt", "Key", "Key_Tab").
    """
    last_error = None
    for path in paths:
        try:
            obj = root
            for name in path:
                obj = getattr(obj, name)
            return obj
        except AttributeError as exc:
            last_error = exc
    if last_error is None:
        raise AttributeError("qt_attr() requires at least one path")
    raise last_error


def qapp_exec(app):
    exec_fn = getattr(app, "exec", None) or getattr(app, "exec_", None)
    if exec_fn is None:
        raise AttributeError("QApplication has no exec/exec_ method")
    return exec_fn()

