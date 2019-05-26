# Do a visualisation of DeepRacer logs.

import parse_logs as pl
import pygame                   # 2d games engine.
import imageio
import os



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
        self.trackdrawn=0
        self.lines=[]
		
		
        # Define the colors we will use in RGB format.
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = pygame.Color(0, 0, 255,50)
        self.GREEN = (0, 153, 0)
        self.RED = pygame.Color(255, 0, 0,50)
        self.YELLOW = (255, 255,0)
       

        # Set the height and width of the viewport.
        self.viewport_size = [800, 600]
        self.track_width=45;
        		
        self.border = 100                        # Number of pixels border around track & car.
		#self.car_template =[[0],[5]]

        self.viewport = pygame.display.set_mode(self.viewport_size)
        
        self.rendered_track=pygame.display.set_mode(self.viewport_size)
        self.car_pic = pygame.image.load(os.path.join('img', 'carsmall.png')).convert_alpha()

        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        self.myfont = pygame.font.SysFont('Courier New', 20)

        pygame.display.set_caption('DeepRacer Visualisation')
        #self.make_gif();

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
            if count>=len(self.track.waypoints)/100 and paint<=len(self.track.waypoints)/100:
                pygame.draw.line(img, self.YELLOW, self.track_to_viewport(line_from,1), self.track_to_viewport(line_to,1), 5)
                paint+=1
                print('paint '+ str( paint))
                if (paint>=len(self.track.waypoints)/100):
                    paint=0;
                    count=0;
            prev = wp
      
       # copy track for rendering calls
        self.rendered_track=pygame.transform.scale(img, (tw[0], tw[1]))
      
       # never do all that again
        self.trackdrawn=1
           

    def draw_car(self, state):
        car = dict_coord_to_list(state)
		
        if state['all_wheels_on_track']:
            colour = self.BLUE
        else:
            colour = self.RED
        
        car_pic=pygame.transform.rotate(self.car_pic, state['heading']+90)
        carposX=self.track_to_viewport(car,1)[0]-car_pic.get_width()/2;
        carposY=self.track_to_viewport(car,1)[1]-car_pic.get_height()/2;
        self.viewport.blit(car_pic, [carposX,carposY])
        pygame.draw.circle(self.viewport, colour, self.track_to_viewport(car,1), 5)


    def white_text(self, text, x, y):
        textsurface = self.myfont.render(text, False, self.WHITE)
        self.viewport.blit(textsurface, (x, y))

    def draw_info_box(self, state):
        self.white_text('Speed = ' + str(state['speed']), 10, 10)
        self.white_text('Heading = ' + '{0:.2f}'.format(state['heading']), 10, 35)
        self.white_text('Steering Angle = ' + '{0:.2f}'.format(state['steering_angle']), 10, 60)


    def draw_all_elements(self, state):
        # Clear the screen and set the screen background
        self.viewport.fill(self.GREEN)
        self.viewport.fill
        self.viewport.set_alpha(255)

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

        for s in self.track.statuses[10:30]:                  # Take a nice set of statuses to make into the GIF.
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
