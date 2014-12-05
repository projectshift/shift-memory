from unittest import TestCase, mock
from nose.plugins.attrib import attr

import arrow
from datetime import datetime, tzinfo
import shiftmemory.times as time
from shiftmemory.exceptions import ValueException

class TimeTest(TestCase):
    """
    Time tests
    This holds test for time conversion utilities
    """

    def test_expires_timestamp_not_processed(self):
        """ Skip conversion if already a timestamp """
        timestamp = '1417762828'
        self.assertEqual(int(timestamp), time.expires_to_timestamp(timestamp))


    def test_get_timezone_name_from_arrow_date(self):
        """ Can get timezone name from arrow date """
        a = arrow.get(datetime.utcnow())
        tz = a.tzinfo.tzname(a)
        self.assertEqual('UTC', tz)


    def test_expires_datetime_to_timestamp(self):
        """ Converting expiration datetime to timestamp """

        now = datetime.now()
        utc = datetime.utcnow()
        msk = arrow.now().to('Europe/Moscow').datetime

        timestamp = int(datetime.utcnow().timestamp())

        self.assertEqual(timestamp, time.expires_to_timestamp(now))
        self.assertEqual(timestamp, time.expires_to_timestamp(utc))
        self.assertEqual(timestamp, time.expires_to_timestamp(msk))


    def test_expires_arrow_to_timestamp(self):
        """ Converting expiration arrow instance to timestamp """

        utc = arrow.now()
        msk = arrow.now().to('Europe/Moscow')

        timestamp = int(datetime.utcnow().timestamp())

        self.assertEqual(timestamp, time.expires_to_timestamp(utc))
        self.assertEqual(timestamp, time.expires_to_timestamp(msk))


    def test_expires_date_string_to_timestamp(self):
        """ Converting expiration date string to timestamp """

        dates = [
            '2012-12-12 20:12:11',
            '2012-12-12T20:12:11',
            '2012-12-12@20:12:11',
            '2012-12-12',
            '2012-12'
            '2012-12',
        ]

        for date in dates:
            result = time.expires_to_timestamp(date)
            self.assertIsInstance(result, int)

    def test_expires_time_shift_to_timestamp(self):
        """ Converting expiration time shift to timestamp """
        shifts = [
            '+1hour',
            '+1 hour',
            '+2hours',
            '+1 day',
            '+2days',
            '+1week -12seconds',
            '+1day 12hours',
            '+1Year2Days',
        ]


        for shift in shifts:
            result = time.expires_to_timestamp(shift)
            self.assertTrue(type(result) is int)



    def test_time_shift_to_params(self):
        """ Time shift string to parameters dict """

        shift = '+2day-12years10 Seconds + 2 months'
        result = time.time_shift_to_params(shift)
        self.assertTrue(type(result) is dict)
        self.assertEqual(-12, result['years'])
        self.assertEqual(+2, result['months'])
        self.assertEqual(+2, result['days'])
        self.assertEqual(-10, result['seconds'])


    def test_raise_when_using_invalid_time_shift(self):
        """ Raise on using invalid time shift """
        invalid = [
            '+2zz',
            'zz',
            '-zz',
            '-3'
        ]
        for shift in invalid:
            with self.assertRaises(ValueException):
                time.time_shift_to_params(shift)


    def test_ttl_from_expiration(self):
        """ Getting ttl from expiration in general way """

        # datetime
        self.assertEquals(0, time.ttl_from_expiration(datetime.utcnow()))

        # timestamp
        ts = int(datetime.utcnow().timestamp())
        self.assertEqual(0, time.ttl_from_expiration(ts))

        # time shift
        expire = '+1day 1minute -10seconds'
        expected = 60*60*24 + 60 - 10
        self.assertEqual(expected, time.ttl_from_expiration(expire))




