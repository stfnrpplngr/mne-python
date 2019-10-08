"""Core visualization operations."""

# Authors: Alexandre Gramfort <alexandre.gramfort@inria.fr>
#          Eric Larson <larson.eric.d@gmail.com>
#          Joan Massich <mailsik@gmail.com>
#          Guillaume Favelier <guillaume.favelier@gmail.com>
#
# License: Simplified BSD

from contextlib import contextmanager
import importlib
import sys

from ._utils import _get_backend_based_on_env_and_defaults, VALID_3D_BACKENDS
from ...utils import logger
from ...utils.check import _check_option

try:
    MNE_3D_BACKEND
    MNE_3D_BACKEND_TEST_DATA
except NameError:
    MNE_3D_BACKEND = _get_backend_based_on_env_and_defaults()
    MNE_3D_BACKEND_TEST_DATA = None

logger.info('Using %s 3d backend.\n' % MNE_3D_BACKEND)

_fromlist = ('_Renderer', '_Projection', '_close_all', '_check_figure')
_name_map = dict(mayavi='_pysurfer_mayavi', pyvista='_pyvista')
if MNE_3D_BACKEND in VALID_3D_BACKENDS:
    # This is (hopefully) the equivalent to:
    #    from ._whatever_name import ...
    _mod = importlib.__import__(
        _name_map[MNE_3D_BACKEND], {'__name__': __name__},
        level=1, fromlist=_fromlist)
    for key in _fromlist:
        locals()[key] = getattr(_mod, key)


def set_3d_backend(backend_name):
    """Set the backend for MNE.

    The backend will be set as specified and operations will use
    that backend.

    Parameters
    ----------
    backend_name : str
        The 3d backend to select. See Notes for the capabilities of each
        backend.

    Notes
    -----
    This table shows the capabilities of each backend ("✓" for full support,
    and "-" for partial support):

    .. table::
       :widths: auto

       +--------------------------------------+--------+---------+
       | 3D function:                         | mayavi | pyvista |
       +======================================+========+=========+
       | :func:`plot_source_estimates`        | ✓      |         |
       +--------------------------------------+--------+---------+
       | :func:`plot_alignment`               | ✓      | ✓       |
       +--------------------------------------+--------+---------+
       | :func:`plot_sparse_source_estimates` | ✓      | ✓       |
       +--------------------------------------+--------+---------+
       | :func:`plot_evoked_field`            | ✓      | ✓       |
       +--------------------------------------+--------+---------+
       | :func:`plot_sensors_connectivity`    | ✓      |         |
       +--------------------------------------+--------+---------+
       | :func:`snapshot_brain_montage`       | ✓      | -       |
       +--------------------------------------+--------+---------+
       +--------------------------------------+--------+---------+
       | **3D feature:**                                         |
       +--------------------------------------+--------+---------+
       | Large data                           | ✓      | ✓       |
       +--------------------------------------+--------+---------+
       | Opacity/transparency                 | ✓      | ✓       |
       +--------------------------------------+--------+---------+
       | Support geometric glyph              | ✓      | ✓       |
       +--------------------------------------+--------+---------+
       | Jupyter notebook                     | ✓      | ✓       |
       +--------------------------------------+--------+---------+
       | Interactivity in Jupyter notebook    | ✓      | ✓       |
       +--------------------------------------+--------+---------+
       | Smooth shading                       | ✓      | ✓       |
       +--------------------------------------+--------+---------+
       | Subplotting                          | ✓      |         |
       +--------------------------------------+--------+---------+
       | Eye-dome lighting                    |        |         |
       +--------------------------------------+--------+---------+
       | Exports to movie/GIF                 |        |         |
       +--------------------------------------+--------+---------+

    """
    _check_option('backend_name', backend_name, VALID_3D_BACKENDS)
    global MNE_3D_BACKEND
    MNE_3D_BACKEND = backend_name
    importlib.reload(sys.modules[__name__])


def get_3d_backend():
    """Return the backend currently used.

    Returns
    -------
    backend_used : str
        The 3d backend currently in use.
    """
    return MNE_3D_BACKEND


@contextmanager
def use_3d_backend(backend_name):
    """Create a viz context.

    Parameters
    ----------
    backend_name : str
        The 3d backend to use in the context.
    """
    old_backend = get_3d_backend()
    set_3d_backend(backend_name)
    try:
        yield
    finally:
        set_3d_backend(old_backend)


@contextmanager
def _use_test_3d_backend(backend_name):
    """Create a testing viz context.

    Parameters
    ----------
    backend_name : str
        The 3d backend to use in the context.
    """
    with use_3d_backend(backend_name):
        global MNE_3D_BACKEND_TEST_DATA
        MNE_3D_BACKEND_TEST_DATA = True
        yield


def set_3d_view(figure, azimuth=None, elevation=None,
                focalpoint=None, distance=None):
    """Configure the view of the given scene.

    Parameters
    ----------
    figure:
        The scene which is modified.
    azimuth: float
        The azimuthal angle of the view.
    elevation: float
        The zenith angle of the view.
    focalpoint: tuple, shape (3,)
        The focal point of the view: (x, y, z).
    distance: float
        The distance to the focal point.
    """
    _mod._set_3d_view(figure=figure, azimuth=azimuth,
                      elevation=elevation, focalpoint=focalpoint,
                      distance=distance)


def set_3d_title(figure, title, size=40):
    """Configure the title of the given scene.

    Parameters
    ----------
    figure:
        The scene which is modified.
    title:
        The title of the scene.
    size: int
        The size of the title.
    """
    _mod._set_3d_title(figure=figure, title=title, size=size)


def create_3d_figure(size, bgcolor=(0, 0, 0), handle=None):
    """Return an empty figure based on the current 3d backend.

    Parameters
    ----------
    size: tuple
        The dimensions of the 3d figure (width, height).
    bgcolor: tuple
        The color of the background.
    handle: int | None
        The figure identifier.

    Returns
    -------
    figure:
        The requested empty scene.
    """
    renderer = _mod._Renderer(fig=handle, size=size, bgcolor=bgcolor)
    return renderer.scene()
