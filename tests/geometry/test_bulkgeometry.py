import numpy as np
import pandas as pd
from numpy.testing import assert_array_equal, assert_array_almost_equal

from tyssue import config
from tyssue.core import Epithelium
from tyssue.generation import (
    three_faces_sheet,
    extrude,
    hexa_grid3d,
    hexa_grid2d,
    subdivide_faces,
)
from tyssue.geometry.bulk_geometry import BulkGeometry, MonoLayerGeometry


def test_bulk_update_vol():

    datasets_2d, _ = three_faces_sheet(zaxis=True)
    datasets = extrude(datasets_2d, method="translation")
    specs = config.geometry.bulk_spec()
    eptm = Epithelium("test_volume", datasets, specs, coords=["x", "y", "z"])

    BulkGeometry.update_all(eptm)

    expected_cell_df = pd.DataFrame.from_dict(
        {
            "cell": [0, 1, 2],
            "x": [0.5, -1.0, 0.5],
            "y": [8.660000e-01, -6.167906e-18, -8.6600000e-01],
            "z": [-0.5, -0.5, -0.5],
            "is_alive": [True, True, True],
            "num_faces": [8, 8, 8],
            "vol": [2.598, 2.598, 2.598],
        }
    ).set_index("cell")

    expected_face_centroids = pd.DataFrame.from_dict(
        {
            "face": list(range(24)),
            "x": [
                0.5,
                -1.0,
                0.5,
                0.5,
                -1.0,
                0.5,
                0.5,
                1.25,
                1.25,
                0.5,
                -0.25,
                -0.25,
                -0.25,
                -1.0,
                -1.75,
                -1.75,
                -1.0,
                -0.25,
                -0.25,
                -0.25,
                0.5,
                1.25,
                1.25,
                0.5,
            ],
            "y": [
                0.86599999999999999,
                0.0,
                -0.86599999999999999,
                0.86599999999999999,
                0.0,
                -0.86599999999999999,
                0.0,
                0.433,
                1.2989999999999999,
                1.732,
                1.2989999999999999,
                0.433,
                0.433,
                0.86599999999999999,
                0.433,
                -0.433,
                -0.86599999999999999,
                -0.433,
                -0.433,
                -1.2989999999999999,
                -1.732,
                -1.2989999999999999,
                -0.433,
                0.0,
            ],
            "z": [
                0.0,
                0.0,
                0.0,
                -1.0,
                -1.0,
                -1.0,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
                -0.5,
            ],
        }
    ).set_index("face")

    ## only update class methods in BulkGeometry : update_vol, update_centroids
    tolerance = 1e-16

    ## check volumes
    assert all((expected_cell_df["vol"] - eptm.cell_df["vol"]) ** 2 < tolerance)

    ## check centroids
    assert all(
        (expected_face_centroids - eptm.face_df.loc[:, ["x", "y", "z"]]) ** 2
        < tolerance
    )


def test_mono_update_perimeters():
    datasets_2d, _ = three_faces_sheet(zaxis=True)
    datasets = extrude(datasets_2d, method="translation")
    specs = config.geometry.bulk_spec()
    eptm = Epithelium("test_volume", datasets, specs, coords=["x", "y", "z"])

    # This method requires a column 'subdiv' in the edge_df.
    # I'm not sure how to build it or what is expected
    # to be found in this column by the method ?

    # MonoLayerGeometry.update_all(eptm)
