# Do a visualisation of DeepRacer logs.

import parse_logs as pl
import cartesian_coordinates as cc
import pygame                           # 2d games engine.
import imageio                          # For making animated GIFs.
import math


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
        self.BLACK = (50, 50, 50)
        self.WHITE = (255, 255, 255)
        self.BLUE = pygame.Color(0, 0, 255,200)
        self.GREEN = (0, 153, 0)
        self.DARKGREEN = (222, 222, 222)
        self.RED = pygame.Color(255, 0, 0,200)
        self.YELLOW = (255, 255,0)
        self.trackdrawn=0
        self.track_width=50

        # Set the height and width of the viewport.
        self.viewport_size = [800, 600]
        self.border = 100                        # Number of pixels border around track & car.

        self.viewport = pygame.display.set_mode(self.viewport_size)

        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        self.myfont = pygame.font.SysFont('Courier New', 20)

        pygame.display.set_caption('DeepRacer Visualisation')

        self.NCOT =0
        self.QNCOT=0
        self.HIRD=0
        self.TH=0
        self.GS=0
        self.GF=0
        self.GSL=0
        self.CC=0

    def bool_to_colour(self, truth):
        if truth:
            return self.DARKGREEN
        else:
            return self.RED

    # Function to convert parm coords in track coordinate space into viewport coordinate space.
    def track_to_viewport(self, t_coords, should_add_border):
        [track_x, track_y] = t_coords
		
        border=0
		
        if should_add_border:
             border=self.border

        vp_x_space = self.viewport_size[0] - 2 * border    # Amount of space on x dim that can be rendered to.
        vp_x = border + int(track_x * vp_x_space / (self.track.max_x - self.track.min_x))

        vp_y_space = self.viewport_size[1] - 2 * border    # Amount of space on y dim that can be rendered to.
        vp_y = self.viewport_size[1] - int(track_y * vp_y_space / (self.track.max_y - self.track.min_y)) - border

        return [vp_x, vp_y]
   

    def draw_track(self):
        
        if self.trackdrawn:
			# no need to draw everything again
            self.viewport.blit(self.rendered_track, [0,0])
            return
        prev = self.track.waypoints[-1]             # Initialise previous to last waypoint.
        tw=self.track_to_viewport([self.track.max_x,self.track.min_y],0)
        
		 # need transparent surface
        img = pygame.Surface(tw, pygame.SRCALPHA, 32)
        img = img.convert_alpha()
		
		#draw track limits white using circles, Perfect pi distances for width - no silly scaling and you could have varable widths if needed 
        for wp in self.track.waypoints:
            line_from = dict_coord_to_list(prev)
            pygame.draw.circle(img, self.WHITE, self.track_to_viewport(line_from,1), (self.track_width/2)+3)
            prev = wp
		#As above but this time overlay track in black	
        for wp in self.track.waypoints:
            line_from = dict_coord_to_list(prev)
            # draw track over outer limits
            pygame.draw.circle(img, self.BLACK, self.track_to_viewport(line_from,1), self.track_width/2)
            prev = wp
		# Finally draw center lines at intervals of wp/100 dashes	
        count=0
        paint=0
        for wp in self.track.waypoints:
            line_from = dict_coord_to_list(prev)
            line_to = dict_coord_to_list(wp)
            count+=1
            print(paint)
            if count>=len(self.track.waypoints)/60 and paint<=len(self.track.waypoints)/60:
                pygame.draw.line(img, self.YELLOW, self.track_to_viewport(line_from,1), self.track_to_viewport(line_to,1), 5)
                paint+=1
                print('paint '+ str( paint))
                if (paint>=len(self.track.waypoints)/60):
                    paint=0;
                    count=0;
            prev = wp
      
       # copy track for rendering calls
        self.rendered_track=pygame.transform.scale(img, (tw[0], tw[1]))
      
       # never do all that again
        self.trackdrawn=1

    def draw_car(self, state):
        car_vertices = {'tail': [-2.0, 0.0],
                        'nose': [2.5, 0.0],
                        'bl_hub': [-2.0, -1.0],
                        'bl_tyre1': [-3.0, -1.0],
                        'bl_tyre2': [-1.0, -1.0],
                        'fl_hub': [2.0, -1.0],
                        'fl_tyre1': [1.0, -1.0],
                        'fl_tyre2': [3.0, -1.0],
                        'br_hub': [-2.0, 1.0],
                        'br_tyre1': [-3.0, 1.0],
                        'br_tyre2': [-1.0, 1.0],
                        'fr_hub': [2.0, 1.0],
                        'fr_tyre1': [1.0, 1.0],
                        'fr_tyre2': [3.0, 1.0]}

        car_edges = [('tail', 'nose'),
                     ('bl_hub', 'br_hub'),
                     ('fl_hub', 'fr_hub'),
                     ('bl_tyre1', 'bl_tyre2'),
                     ('fl_tyre1', 'fl_tyre2'),
                     ('br_tyre1', 'br_tyre2'),
                     ('fr_tyre1', 'fr_tyre2')]

        car_coord = dict_coord_to_list(state)

        new_vertices = {}
		
		#get hub position
        fl_hub_vertex=None
        fr_hub_vertex=None
        for key in car_vertices:
            if key in ['fl_hub', 'fr_hub']:
			    val = car_vertices[key]
			    rotated = cc.rotate_around_origin(val, - state['heading'])
			    scaled = cc.scale(rotated, 0.07)                         # Tracks coordinate scale is tiny!
			    translated = cc.translation(scaled, car_coord)          # Move the vertex to the car's coord on track.
			    # The front hub positions will be needed later, for rotating front tyres around,
			    # so set variables to remember them.
			    if key == 'fl_hub':
			        fl_hub_vertex = translated
			    elif key == 'fr_hub':
				fr_hub_vertex = translated
			
        for key in car_vertices:
            val = car_vertices[key]

            rotated = cc.rotate_around_origin(val, - state['heading'])

            scaled = cc.scale(rotated, 0.07)                         # Tracks coordinate scale is tiny!
            translated = cc.translation(scaled, car_coord)          # Move the vertex to the car's coord on track.
			
            # If this vertex is part of a front tyre, then it needs to be rotated around it's hub.
            if key in ['fl_tyre1', 'fl_tyre2']:
                translated = cc.rotate_around_a_point(translated, fl_hub_vertex, - state['steering_angle'])
            elif key in ['fr_tyre1', 'fr_tyre2']:
                translated = cc.rotate_around_a_point(translated, fr_hub_vertex, - state['steering_angle'])

            new_vertices[key] = translated

        for (k1, k2) in car_edges:
            v1 = new_vertices[k1]
            v2 = new_vertices[k2]

            pygame.draw.line(
                self.viewport,
                self.bool_to_colour(state['all_wheels_on_track']),
                self.track_to_viewport(v1,1),
                self.track_to_viewport(v2,1),
                5)

    def draw_text(self, text, x, y, colour):
        textsurface = self.myfont.render(text, False, colour)
        self.viewport.blit(textsurface, (x, y))

    def draw_info_box(self, state):
        self.draw_text('Speed = ' + str(state['speed']), 10, 10, self.WHITE)
        self.draw_text('Steps = ' + str(state['steps']), 10, 35, self.WHITE)
        self.draw_text('Reward = ' + str(state['score']), 10, 60, self.WHITE)

        self.draw_text('Near Centre Of Track', 10, 500, self.bool_to_colour(state['near_centre_of_track']))
        if not state['near_centre_of_track']:
            self.NCOT+=1
        self.draw_pie(400,510,self.NCOT)
        self.draw_text('Quite Near Centre Of Track', 10, 525, self.bool_to_colour(state['quite_near_centre_of_track']))
        if not state['quite_near_centre_of_track']:
            self.QNCOT+=1
        self.draw_pie(400,535,self.QNCOT)
        self.draw_text('Heading In Right Direction', 10, 550, self.bool_to_colour(state['heading_in_right_direction']))
        if not state['heading_in_right_direction']:
            self.HIRD+=1
        self.draw_pie(400,560,self.HIRD)
        self.draw_text('Turning Hard', 10, 575, self.bool_to_colour(state['turning_hard']))
        if not state['turning_hard']:
            self.TH+=1
        self.draw_pie(400,585,self.TH)
        self.draw_text('Going Straight', 500, 500, self.bool_to_colour(state['going_straight']))
        if not state['going_straight']:
            self.GS+=1
        self.draw_pie(730,510,self.TH)
        self.draw_text('Going Fast', 500, 525, self.bool_to_colour(state['going_fast']))
        if not state['going_fast']:
            self.GF+=1
        self.draw_pie(730,535,self.GF)
        self.draw_text('Going Slowly', 500, 550, self.bool_to_colour(state['going_slowly']))
        if not state['going_slowly']:
            self.GSL+=1
        self.draw_pie(730,560,self.GSL)
        self.draw_text('Correcting Course', 500, 575, self.bool_to_colour(state['correcting_course']))
        if not state['correcting_course']:
            self.CC+=1
        self.draw_pie(730,585,self.CC)

    def draw_pie(self,posX,posY,val):
        # Center and radius of pie chart
        cx, cy, r = posX, posY, 10
        self.draw_text(str(val), cx+12, cy-10,self.RED)
        # Background circle
        pygame.draw.circle(self.viewport, (0,0,0), (cx, cy), r)

        # Calculate the angle in degrees
        angle = val*360/len(self.track.waypoints)

        # Start list of polygon points
        p = [(cx, cy)]

        # Get points on arc
        for n in range(0,angle):
            x = cx + int(r*math.cos(n*math.pi/180))
            y = cy+int(r*math.sin(n*math.pi/180))
            p.append((x, y))
        p.append((cx, cy))

        # Draw pie segment
        if len(p) > 2:
            pygame.draw.polygon(self.viewport, self.RED, p)


    def draw_all_elements(self, state):
        # Clear the screen and set the screen background
        self.viewport.fill(self.GREEN)

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
            self.NCOT =0
            self.QNCOT=0
            self.HIRD=0
            self.TH=0
            self.GS=0
            self.GF=0
            self.GSL=0
            self.CC=0
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
