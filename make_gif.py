# Make an animated GIF out of a dozen or so statuses.

import visualise_logs as vl

start_track = vl.Track('example_log_start_of_training.txt')
start_track.find_min_max_dimensions()

start_screen = vl.Visualise(start_track)
start_screen.make_gif('start', 'deepracer-start-of-training.gif')


end_track = vl.Track('example_log_end_of_training.txt')
end_track.find_min_max_dimensions()

end_screen = vl.Visualise(end_track)
end_screen.make_gif('end', 'deepracer-end-of-training.gif')