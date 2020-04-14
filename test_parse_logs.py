# Some tests of the log parsing code.

import parse_logs as pl
import unittest


class TestParseLogs(unittest.TestCase):

    def test_filename_to_list_of_strings(self):
        self.assertEqual(pl.filename_to_list_of_strings('example_data_1.txt'), [['This', 'is', 'a'], ['test.']])

    def test_filter_by_2nd_item(self):
        logs = pl.filename_to_list_of_strings('example_short_log.txt')
        filtered_logs = pl.filter_by_2nd_item(logs, 'TRACE_WAYPOINTS')

        for log_entry in filtered_logs:
            self.assertEqual(log_entry[1], 'TRACE_WAYPOINTS')

    def test_make_list_of_waypoints(self):
        logs = pl.filename_to_list_of_strings('example_short_log.txt')
        waypoints_only = pl.filter_by_2nd_item(logs, 'TRACE_WAYPOINTS')
        waypoints = pl.make_list_of_waypoints(waypoints_only)

        for each_dict in waypoints:
            keys_list = list(each_dict.keys())
            keys_list.sort()
            self.assertEqual(keys_list, ['waypoint', 'x', 'y'])

    def test_make_list_of_statuses(self):
        logs = pl.filename_to_list_of_strings('example_short_log.txt')
        statuses_only = pl.filter_by_2nd_item(logs, 'TRACE_STATUS')
        los = pl.make_list_of_statuses(statuses_only)
        self.assertEqual(len(los), 4)


if __name__ == '__main__':
    unittest.main()
