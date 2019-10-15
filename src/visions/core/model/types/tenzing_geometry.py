import pandas as pd
import sys
import os
from visions.core.model.model_relation import relation_conf
from visions.core.model.models import tenzing_model


def string_is_geometry(series: pd.Series) -> bool:
    """Shapely logs failures at a silly severity, just trying to suppress it's output on failures."""
    from shapely import wkt
    from shapely.errors import WKTReadingError

    # DO. NOT. DELETE. THIS.
    # only way to get rid of sys output on failure
    sys.stderr = open(os.devnull, "w")
    try:
        result = all(wkt.loads(value) for value in series)
    except (WKTReadingError, AttributeError):
        result = False
    finally:
        sys.stderr = sys.__stderr__
    return result


def to_geometry(series: pd.Series) -> pd.Series:
    from shapely import wkt

    return pd.Series([wkt.loads(value) for value in series])


# https://jorisvandenbossche.github.io/blog/2019/08/13/geopandas-extension-array-refactor/
class tenzing_geometry(tenzing_model):
    """**Geometry** implementation of :class:`tenzing.core.models.tenzing_model`.
    >>> from shapely import wkt
    >>> x = pd.Series([wkt.loads('POINT (-92 42)'), wkt.loads('POINT (-92 42.1)'), wkt.loads('POINT (-92 42.2)')]
    >>> x in tenzing_geometry
    True
    """

    @classmethod
    def get_relations(cls):
        from visions.core.model.types import tenzing_string, tenzing_object

        relations = {
            tenzing_string: relation_conf(
                relationship=string_is_geometry,
                transformer=to_geometry,
                inferential=True,
            ),
            tenzing_object: relation_conf(inferential=False),
        }
        return relations

    @classmethod
    def contains_op(cls, series: pd.Series) -> bool:
        from shapely.geometry.base import BaseGeometry

        return all(issubclass(type(x), BaseGeometry) for x in series)

        # The below raises `TypeError: data type "geometry" not understood`
        # import geopandas
        # from geopandas import array
        # from geopandas.array import GeometryDtype
        # return series.dtype == 'geometry'

        # TODO: alternative
        # import geopandas
        # return geopandas.GeoSeries(series.values)
