# Do endless animation of car statuses.

import visualise_logs as vl

this_track = vl.Track('example_log_start_of_training.txt')
this_track.find_min_max_dimensions()

screen = vl.Visualise(this_track)
screen.animate()