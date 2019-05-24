# Functions for manipulating cartesian coordinates expressed as [x, y] lists.

import math


# Move, or slide, a coordincate in 2d space.
def translation(vertex, delta):
    [vertex_x, vertex_y] = vertex
    [delta_x, delta_y] = delta
    return [vertex_x + delta_x, vertex_y + delta_y]


# Move a coordinate closer / further from origin.
# If done for all vertices in a 2d shape, it has the effect of changing the size of the whole shape.
def scale(vertex, scale_factor):
    [vertex_x, vertex_y] = vertex
    return [vertex_x * scale_factor, vertex_y * scale_factor]


# https://en.wikipedia.org/wiki/Rotation_of_axes#Derivation
def rotate_around_origin(vertex, rotation_degrees):
    [vertex_x, vertex_y] = vertex
    rotation_radians = math.radians(rotation_degrees)

    return[vertex_x * math.cos(rotation_radians) + vertex_y * math.sin(rotation_radians),
           - vertex_x * math.sin(rotation_radians) + vertex_y * math.cos(rotation_radians)
           ]

# Method has 3 steps,
# 1. Move the vertex so that centre of rotations is now the origin.
# 2. Rotate around origins.
# 3. Do the opposite of move in 1.
def rotate_around_a_point(vertex, pivot, rotation_degrees):
    [pivot_x, pivot_y] = pivot

    moved_vertex = translation(vertex, [-pivot_x, -pivot_y])                    # Step 1.
    rotated_vertex = rotate_around_origin(moved_vertex, rotation_degrees)       # Step 2.
    re_moved_vertex = translation(rotated_vertex, pivot)                      # Step 3.

    return re_moved_vertex
