import numpy as np
from .base_geometry import (update_dcoords, scale,
                            update_length, update_centroid)
from .planar_geometry import update_perimeters


def get_default_geom_specs():
    default_geom_specs = {
        "face": {
            "num_sides": (6, np.int),
            },
        "jv": {
            "rho": (0., np.float),
            "basal_shift": (4., np.float), # previously rho_lumen
            },
        "je": {
            "nx": (0., np.float),
            "ny": (0., np.float),
            "nz": (0., np.float),
            },
        "settings": {
            "geometry": "cylindrical",
            "height_axis": 'z'
            }
        }
    return default_geom_specs


def update_all(sheet, **geom_spec_kw):
    '''
    Updates the sheet geometry by updating:
    * the edge vector coordinates
    * the edge lengths
    * the face centroids
    * the normals to each edge associated face
    * the face areas
    * the vertices heights (depends on geometry)
    * the face volumes (depends on geometry)

    '''
    geom_spec = get_default_geom_specs()
    geom_spec.update(**geom_spec_kw)

    update_dcoords(sheet)
    update_length(sheet)
    update_centroid(sheet)
    if geom_spec['settings']['geometry'] == 'cylindrical':
        update_height_cylindrical(sheet,
                                  geom_spec['settings'])
    elif geom_spec['settings']['geometry'] == 'flat':
        update_height_flat(sheet, geom_spec['settings'])
    update_normals(sheet)
    update_areas(sheet)
    update_perimeters(sheet)
    update_vol(sheet)


def update_normals(sheet):
    '''
    Updates the face_df `coords` columns as the face's vertices
    center of mass.
    '''
    coords = sheet.coords
    face_pos = sheet.upcast_face(sheet.face_df[coords]).values
    srce_pos = sheet.upcast_srce(sheet.jv_df[coords]).values
    trgt_pos = sheet.upcast_trgt(sheet.jv_df[coords]).values

    normals = np.cross(srce_pos - face_pos, trgt_pos - srce_pos)
    sheet.je_df[sheet.ncoords] = normals


def update_areas(sheet):
    '''
    Updates the normal coordniate of each (srce, trgt, face) face.
    '''
    sheet.je_df['sub_area'] = np.linalg.norm(sheet.je_df[sheet.ncoords],
                                             axis=1) / 2
    sheet.face_df['area'] = sheet.sum_face(sheet.je_df['sub_area'])


def update_vol(sheet):
    '''
    Note that this is an approximation of the sheet geometry
    module.

    '''
    sheet.je_df['sub_vol'] = (sheet.upcast_srce(sheet.jv_df['height']) *
                              sheet.je_df['sub_area'])
    sheet.face_df['vol'] = sheet.sum_face(sheet.je_df['sub_vol'])

# ### Cylindrical geometry specific

def update_height_cylindrical(sheet, settings):
    '''
    Updates each face height in a cylindrical geometry.
    e.g. face anchor is assumed to lie at a distance
    `parameters['basal_shift']` from the third axis of
    the triplet `coords`
    '''
    w = settings['height_axis']
    u, v = (c for c in sheet.coords if c != w)
    sheet.jv_df['rho'] = np.hypot(sheet.jv_df[v],
                                  sheet.jv_df[u])
    sheet.jv_df['height'] = (sheet.jv_df['rho'] -
                             sheet.jv_df['basal_shift'])


# ### Flat geometry specific

def update_height_flat(sheet, settings):
    '''
    Updates each face height in a flat geometry.
    e.g. face anchor is assumed to lie at a distance
    `parameters['basal_shift']` from the plane where
    the coordinate `coord` is equal to 0
    '''
    coord = settings['height_axis']
    sheet.jv_df['rho'] = sheet.jv_df[coord]
    sheet.jv_df['height'] = sheet.jv_df[coord] - sheet.jv_df['basal_shift']