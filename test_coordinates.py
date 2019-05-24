# A set of tests for the cartesian coordinates functions.

import cartesian_coordinates as cc

v1 = [2.0, 3.0]
v2 = [1.0, 0.0]

print(v1, 'Translate [10.0, 11.0]', cc.translation(v1, [10.0, 11.0]))

print(v1, 'Scale 5', cc.scale(v1, 5))

print(v2, 'Rotate 90', cc.rotate_around_origin(v2, 90))
print(v2, 'Rotate -45', cc.rotate_around_origin(v2, -45.0))

print(v1, 'Rotate 90 around [2.0, 2.0]', cc.rotate_around_a_point(v1, [2.0, 2.0], 90.0))
