# Some tests of the log parsing code.

import parse_logs as pl

def test1():
    print(pl.filename_to_list_of_strings('test_data_1.txt'))


def test2():
    logs = pl.filename_to_list_of_strings('simulation_log.txt')
    print(pl.filter_by_2nd_item(logs, 'TRACE_WAYPOINTS'))


def test3():
    logs = pl.filename_to_list_of_strings('simulation_log.txt')
    waypoints_only = pl.filter_by_2nd_item(logs, 'TRACE_WAYPOINTS')
    print(pl.make_list_of_waypoints(waypoints_only))


def test4():
    logs = pl.filename_to_list_of_strings('simulation_log.txt')
    statuses_only = pl.filter_by_2nd_item(logs, 'TRACE_STATUS')
    los = pl.make_list_of_statuses(statuses_only)
    print(len(los))
