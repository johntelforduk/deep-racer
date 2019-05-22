

# Open the parm filename. Read each line of the file, splitting each line into a list of strings delimited by space.
# The function output is a list of list of stings.
#
# Eg. input file,
# ---------------
# This is a
# test.
# ---------------
def filename_to_list_of_strings(filename):
    output = []
    with open(filename) as fileobj:
        for line in fileobj:
            output.append((line.replace('\n', '')).split(' '))
    return output


# For example,
# input_list = [['foo', 'bar', 'harry'], ['foo', 'miss', 'david']]
# target = 'bar'
# output = [['foo', 'bar', 'harry']]
def filter_by_2nd_item(input_list, target):
    output = []
    for item in input_list:
        if item[1] == target:
            output.append(item)
    return output


# Make a list of waypoints out of filtered list of waypoint strings.
def make_list_of_waypoints(input_list):
    output = []
    pos = -1

    for item in input_list[0]:                            # Every item in the list is same, so arbitrarily pick 1st one.
        pos += 1

        if pos >= 2:                                    # Ignore the first two items in the list,
            tuple_pos = (pos - 2) % 3

            if tuple_pos == 0:
                i1 = item
            elif tuple_pos == 1:
                i2 = item
            else:
                waypoint = {}
                waypoint['waypoint'] = int(i1)
                waypoint['x'] = float(i2)
                waypoint['y'] = float(item)
                output.append(waypoint)             # Append the tuple.
    return output


# 'true' -> True, 'false' -> False
def string_to_bool(s):
    return s == 'true'


def make_list_of_statuses(input_list):
    output = []

    for s in input_list:
        status = {}
        status['timestamp'] = float(s[2])
        status['all_wheels_on_track'] = string_to_bool(s[3])
        status['x'] = float(s[4])
        status['y'] = float(s[5])
        status['distance_from_center'] = float(s[6])
        status['is_left_of_center'] = string_to_bool(s[7])
        status['heading'] = float(s[8])
        status['progress'] = float(s[9])
        status['steps'] = int(s[10])
        status['speed'] = float(s[11])
        status['steering_angle'] = float(s[12])
        status['track_width'] = float(s[13])
        status['max_speed'] = float(s[14])
        status['max_steer'] = float(s[15])
        status['near_centre_of_track'] = string_to_bool(s[16])
        status['quite_near_centre_of_track'] = string_to_bool(s[17])
        status['heading_in_right_direction'] = string_to_bool(s[18])
        status['turning_hard'] = string_to_bool(s[19])
        status['going_straight'] = string_to_bool(s[20])
        status['going_fast'] = string_to_bool(s[21])
        status['going_slowly'] = string_to_bool(s[22])
        status['correcting_course'] = string_to_bool(s[23])
        status['rule_number'] = int(s[24])
        status['rule_description'] = s[25].replace('_', ' ')
        status['reward_level'] = s[26].replace('_', ' ')
        status['score'] = float(s[27])

        output.append(status)

    return output
