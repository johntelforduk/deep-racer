# Do endless animation of car statuses.

import visualise_logs as vl

this_track = vl.Track('truncated_simulation_log.txt')
this_track.find_min_max_dimensions()

screen = vl.Visualise(this_track)
screen.animate()