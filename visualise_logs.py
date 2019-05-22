# Do a visualisation of DeepRacer logs.

import parse_logs as pl
import pygame                   # 2d games engine.
import imageio


# Convert coordinates from dictionary (as used by logs) to list of co-ordinates (as used by pygame).
def dict_coord_to_list(dict_coord):
    list_coord = []
    list_coord.append(dict_coord['x'])
    list_coord.append(dict_coord['y'])
    return list_coord


class Track:

    def __init__(self, filename):

        big_float = 100000.0

        # These max and min are across all waypoints and car positions.
        self.min_x = big_float                      # Easy for minimum to be less than this.
        self.max_x = -big_float                     # Easy for maximum to be more than this.
        self.min_y = big_float
        self.max_y = -big_float

        logs = pl.filename_to_list_of_strings(filename)
        waypoints_only = pl.filter_by_2nd_item(logs, 'TRACE_WAYPOINTS')
        statuses_only = pl.filter_by_2nd_item(logs, 'TRACE_STATUS')

        self.waypoints = pl.make_list_of_waypoints(waypoints_only)
        self.statuses = pl.make_list_of_statuses(statuses_only)

        self.start_time = (self.statuses[0])['timestamp']

    def find_min_max_dimensions(self):
        # First look for min and max in waypoints list.
        for w in self.waypoints:
            if w['x'] < self.min_x:
                self.min_x = w['x']
            if w['x'] > self.max_x:
                self.max_x = w['x']
            if w['y'] < self.min_y:
                self.min_y = w['y']
            if w['y'] > self.max_y:
                self.max_y = w['y']

        # Now look for min and max in statuses list.
        for s in self.statuses:
            if s['x'] < self.min_x:
                self.min_x = s['x']
            if s['x'] > self.max_x:
                self.max_x = s['x']
            if s['y'] < self.min_y:
                self.min_y = s['y']
            if s['y'] > self.max_y:
                self.max_y = s['y']


class Visualise:

    def __init__(self, track):

        # Initialize the game engine.
        pygame.init()

        self.track = track

        # Define the colors we will use in RGB format.
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)

        # Set the height and width of the viewport.
        self.viewport_size = [800, 600]
        self.border = 100                        # Number of pixels border around track & car.

        self.viewport = pygame.display.set_mode(self.viewport_size)

        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        self.myfont = pygame.font.SysFont('Courier New', 20)

        pygame.display.set_caption('DeepRacer Visualisation')

    # Function to convert parm coords in track coordinate space into viewport coordinate space.
    def track_to_viewport(self, t_coords):
        [track_x, track_y] = t_coords

        vp_x_space = self.viewport_size[0] - 2 * self.border    # Amount of space on x dim that can be rendered to.
        vp_x = self.border + int(track_x * vp_x_space / (self.track.max_x - self.track.min_x))

        vp_y_space = self.viewport_size[1] - 2 * self.border    # Amount of space on y dim that can be rendered to.
        vp_y = self.viewport_size[1] - int(track_y * vp_y_space / (self.track.max_y - self.track.min_y)) - self.border

        return [vp_x, vp_y]


    def draw_track(self):
        prev = self.track.waypoints[-1]             # Initialise previous to last waypoint.

        for wp in self.track.waypoints:
            line_from = dict_coord_to_list(prev)
            line_to = dict_coord_to_list(wp)

            pygame.draw.line(self.viewport, self.BLUE, self.track_to_viewport(line_from), self.track_to_viewport(line_to), 5)

            prev = wp

    def draw_car(self, state):
        car = dict_coord_to_list(state)
        if state['all_wheels_on_track']:
            colour = self.GREEN
        else:
            colour = self.RED

        pygame.draw.circle(self.viewport, colour, self.track_to_viewport(car), 5)


    def white_text(self, text, x, y):
        textsurface = self.myfont.render(text, False, self.WHITE)
        self.viewport.blit(textsurface, (x, y))

    def draw_info_box(self, state):
        self.white_text('Speed = ' + str(state['speed']), 10, 10)
        self.white_text('Heading = ' + '{0:.2f}'.format(state['heading']), 10, 35)
        self.white_text('Steering Angle = ' + '{0:.2f}'.format(state['steering_angle']), 10, 60)


    def draw_all_elements(self, state):
        # Clear the screen and set the screen background
        self.viewport.fill(self.BLACK)

        self.draw_track()
        self.draw_info_box(state)
        self.draw_car(state)

        pygame.display.flip()

    # Do animation of all statuses, showing car going around the track.
    def animate(self):
        # Loop until the user clicks the close button.
        done = False
        clock = pygame.time.Clock()

        while not done:

            for s in self.track.statuses:

                # This limits the while loop to a max of 10 times per second.
                # Leave this out and we will use all CPU we can.
                clock.tick(10)

                for event in pygame.event.get():  # User did something
                    if event.type == pygame.QUIT:  # If user clicked close
                        done = True  # Flag that we are done so we exit this loop

                self.draw_all_elements(s)

                if done:
                    break

        # Be IDLE friendly
        pygame.quit()

    # For the first 10 statuses, draw them onscreen, and save each one to a screenshot .PNG file.
    # Then make an animated GIF out of the screenshots.
    def make_gif(self):
        counter = 1
        filenames = []

        for s in self.track.statuses[4:16]:                  # Take a nice set of statuses to make into the GIF.
            self.draw_all_elements(s)

            screenshot_name = 'screenshots/screenshot' + format(counter, '02') + '.png'
            pygame.image.save(self.viewport, screenshot_name)

            filenames.append(screenshot_name)
            counter += 1
        pygame.quit()

        images = []
        for filename in filenames:
            images.append(imageio.imread(filename))
        imageio.mimsave('screenshots/deepracer-movie.gif', images)
