

import math
import time


def bool_to_string(b):
    if b:
        return "true"
    else:
        return "false"



class Environment:

    def __init__(self, params):

        # Extract some variables from the params.
        # See this page for details,
        # https://docs.aws.amazon.com/deepracer/latest/developerguide/deepracer-reward-function-input.html
        self.all_wheels_on_track = params['all_wheels_on_track']
        self.x = params['x']
        self.y = params['y']
        self.distance_from_center = params['distance_from_center']
        self.is_left_of_center = params['is_left_of_center']
        self.heading = params['heading']
        self.progress = params['progress']
        self.steps = params['steps']
        self.speed = params['speed']
        self.steering_angle = params['steering_angle']
        self.track_width = params['track_width']
        self.waypoints = params['waypoints']
        self.closest_waypoints = params['closest_waypoints']


class Agent:

    def __init__(self, state):

        # Many of the booleans will default to False. Later methods will set them correctly.
        self.state = state
        self.max_speed = 2.0                            # From Action Space settings.
        self.max_steer = 30.0                           # From Action Space settings.
        self.near_centre_of_track = False
        self.quite_near_centre_of_track = False
        self.heading_in_right_direction = False
        self.turning_hard = False
        self.going_straight = False
        self.going_fast = False
        self.going_slowly = False
        self.correcting_course = False

    # Is car near, or quite near, to centre of the track?
    def check_track_position(self):
        marker_1 = 0.1 * self.state.track_width
        marker_2 = 0.25 * self.state.track_width
        self.near_centre_of_track = (self.state.distance_from_center <= marker_1)
        self.quite_near_centre_of_track = (self.state.distance_from_center <= marker_2)

    # Is the car pointing in the approximate direction that the track is heading?
    def check_direction(self):
        # Calculate the direction of the center line based on the closest waypoints.
        next_point = self.state.waypoints[self.state.closest_waypoints[1]]
        prev_point = self.state.waypoints[self.state.closest_waypoints[0]]

        # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians.
        track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        # Convert to degrees.
        track_direction = math.degrees(track_direction)

        # Calculate the difference between the track direction and the heading direction of the car
        direction_diff = abs(track_direction - self.state.heading)

        # If track direction and car heading are close, set the boolean to True.
        direction_threshold = 10.0
        self.heading_in_right_direction = (direction_diff < direction_threshold)

    # Is the car going fast or slowly?
    def check_speed(self):
        self.going_fast = (self.state.speed > 0.9 * self.max_speed)
        self.going_slowly = (self.state.speed <= 0.51 * self.max_speed)

    # Is the car turning hard or going in straight line?
    def check_steering(self):
        hard_steer = self.max_steer * 0.9
        self.turning_hard = (abs(self.state.steering_angle) > hard_steer)
        self.going_straight = (self.state.steering_angle == 0.0)

    # Is the car correcting course?
    def check_correcting_course(self):
        steering_left = (self.state.steering_angle > 0)
        steering_right = (self.state.steering_angle < 0)
        self.correcting_course = ((self.state.is_left_of_center and steering_right)
                                  or (not self.state.is_left_of_center and steering_left))


class Reward:

    def __init__(self, car):
        self.car = car
        self.rule_number = 0
        self.rule_description = ""
        self.reward_level = ""
        self.score = 0.0

    # A driving rule has been met. Figure out the reward score.
    def rule_met(self, rule_number, rule_description, reward_level):
        self.rule_number = rule_number
        self.rule_description = rule_description
        self.reward_level = reward_level

        reward_map = {"Very Big": 1.0,
                      "Big": 0.75,
                      "Small": 0.45,
                      "Default": 0.1,
                      "Penalise": -1.0}
        self.score = reward_map.get(reward_level)

    def reward_and_punish(self):
        # 0. Start with quite small, default reward.
        self.rule_met(0, "Default.", "Default")

        # 1. Doing OK; not doing great.
        if (self.car.quite_near_centre_of_track
                and not self.car.turning_hard
                and not self.car.going_fast):
            self.rule_met(1, "Doing OK; not doing great.", "Small")

        # 2. Car on track, but not quite near centre, going slowly, steering back towards centre.
        if (self.car.state.all_wheels_on_track
                and not self.car.quite_near_centre_of_track
                and self.car.going_slowly
                and self.car.correcting_course):
            self.rule_met(2, "On track, not quite near centre, slow, steering back towards centre.", "Small")

        # 3. Near centre of track, not straight, but not fast either.
        if (self.car.near_centre_of_track
                and self.car.heading_in_right_direction
                and not self.car.going_straight
                and not self.car.going_fast
                and not self.car.turning_hard):
            self.rule_met(3, "Near centre of track, not straight, but not fast either.", "Small")

        # 4. Cornering nicely around a tight corner.
        if (self.car.turning_hard
                and self.car.quite_near_centre_of_track
                and self.car.heading_in_right_direction
                and self.car.going_slowly):
            self.rule_met(4, "Cornering nicely around a tight corner.", "Big")

        # 5. Middle of track, fast and straight in right direction.
        if (self.car.near_centre_of_track
                and self.car.heading_in_right_direction
                and self.car.going_fast
                and self.car.going_straight):
            self.rule_met(5, "Middle of track, fast and straight in right direction.", "Very Big")

        # 6. Going fast and turning hard.
        if (self.car.going_fast
                and self.car.turning_hard):
            self.rule_met(6, "Going fast and turning hard.", "Penalise")

        # 7. Going fast near edge of track.
        if (self.car.going_fast
                and not self.car.quite_near_centre_of_track):
            self.rule_met(7, "Going fast near edge of track.", "Penalise")

        # 8. At least one wheel off the track.
        if not self.car.state.all_wheels_on_track:
            self.rule_met(8, "At least one wheel off the track.", "Penalise")

    # Send info about status to stdout.
    # AWS will send this to the CLoudWatch logs, /aws/robomaker/SimulationJobs
    def status_out(self):
        print('TRACE_STATUS '
              + str(time.time()) + ' '                                     # Trace items are space delimeted.
              + bool_to_string(self.car.state.all_wheels_on_track) + ' '   # True becomes 'true', False becomes 'false'
              + str(self.car.state.x) + ' '
              + str(self.car.state.y) + ' '
              + str(self.car.state.distance_from_center) + ' '
              + bool_to_string(self.car.state.is_left_of_center) + ' '
              + str(self.car.state.heading) + ' '
              + str(self.car.state.progress) + ' '
              + str(self.car.state.steps) + ' '
              + str(self.car.state.speed) + ' '
              + str(self.car.state.steering_angle) + ' '
              + str(self.car.state.track_width) + ' '
              + str(self.car.max_speed) + ' '
              + str(self.car.max_steer) + ' '
              + bool_to_string(self.car.near_centre_of_track) + ' '
              + bool_to_string(self.car.quite_near_centre_of_track) + ' '
              + bool_to_string(self.car.heading_in_right_direction) + ' '
              + bool_to_string(self.car.turning_hard) + ' '
              + bool_to_string(self.car.going_straight) + ' '
              + bool_to_string(self.car.going_fast) + ' '
              + bool_to_string(self.car.going_slowly) + ' '
              + bool_to_string(self.car.correcting_course) + ' '
              + str(self.rule_number) + ' '
              + self.rule_description.replace(' ', '_') + ' '              # Because space is the delimeter...
              + self.reward_level.replace(' ', '_') + ' '                  # need to replace it with underscore.
              + str(self.score))

    def waypoints_out(self):
        wp = 'TRACE_WAYPOINTS '
        counter = 0
        for [x, y] in self.car.state.waypoints:
            if counter != 0:
                wp = wp + ' '
            wp += str(counter) + ' ' + str(x) + ' ' + str(y)
            counter += 1

        print(wp)


def reward_function(params):

    state = Environment(params)
    car = Agent(state)
    reinforcement = Reward(car)

    car.check_track_position()
    car.check_direction()
    car.check_speed()
    car.check_steering()
    car.check_correcting_course()

    reinforcement.reward_and_punish()
    reinforcement.status_out()
    reinforcement.waypoints_out()

    return float(reinforcement.score)
