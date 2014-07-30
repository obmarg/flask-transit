import os
from dateutil import tz
from StringIO import StringIO
from datetime import datetime, timedelta
from flask import Flask, request, abort
from flask.ext.transit import init_transit, transition
from flask.ext.testing import TestCase
from transit.writer import Writer
from transit.reader import Reader


class TestObj(object):
    def __init__(self, number):
        self.number = number

    def __eq__(self, other):
        return self.number == other.number


class TestObjHandler(object):
    @staticmethod
    def tag(_):
        return "testobj"

    @staticmethod
    def rep(test_obj):
        return test_obj.number

    @staticmethod
    def string_rep(test_obj):
        return str(test_obj.number)

    @staticmethod
    def from_rep(value):
        return TestObj(int(value))


app = Flask('tests')
init_transit(app, {TestObj: TestObjHandler})


def to_transit(in_data, protocol='json'):
    io = StringIO()
    writer = Writer(io, protocol)

    writer.register(TestObj, TestObjHandler)

    writer.write(in_data)
    return io.getvalue()


def from_transit(in_data, protocol):
    io = StringIO(in_data)
    reader = Reader(protocol)

    reader.register("testobj", TestObjHandler)

    return Reader(protocol).read(io)


@app.route('/echo_transit/<protocol>', methods=['POST'])
def echo_transit(protocol):
    return to_transit(request.transit, protocol)


@app.route('/echo_transition/<protocol>', methods=['POST'])
def echo_transition(protocol):
    return transition(request.transit, protocol)


@app.route('/expect_no_transit', methods=['POST'])
def expect_no_transit():
    if request.transit:
        abort(400)
    return 'ok'


class FlaskTransitTests(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def _reading_test(self, in_data, base_url, protocol):
        data = to_transit(in_data, protocol)

        response = self.client.post(
            os.path.join(base_url, protocol),
            data=data,
            headers={'content-type': 'application/transit+' + protocol}
        )

        self.assertEqual(response.data, data)
        self.assertEqual(from_transit(response.data, protocol), in_data)
        return response

    def test_transit_json_reading(self):
        self._reading_test({'hi': 'there',
                            'ls': (1, 2, 3),
                            'aset': frozenset({1, 2, 3})},
                           '/echo_transit/',
                           'json')

    def test_transit_msgpack_reading(self):
        self._reading_test({'hi': 'there',
                            'ls': (1, 2, 3),
                            'aset': frozenset({1, 2, 3})},
                           '/echo_transit/',
                           'msgpack')

    def test_transition_json(self):
        self._reading_test({'hi': 'there',
                            'ls': (1, 2, 3),
                            'aset': frozenset({1, 2, 3})},
                           '/echo_transition/',
                           'json')

    def test_transition_msgpack(self):
        self._reading_test({'hi': 'there',
                            'ls': (1, 2, 3),
                            'aset': frozenset({1, 2, 3})},
                           '/echo_transition/',
                           'msgpack')

    def test_custom_rw_json(self):
        self._reading_test({'hi': 'there',
                            'obj': TestObj(3)},
                           '/echo_transition/',
                           'json')

    def test_custom_rw_msgpack(self):
        self._reading_test({'hi': 'there',
                            'obj': TestObj(100)},
                           '/echo_transition/',
                           'msgpack')

    def _do_datetime_test(self, protocol):
        # datetime tests need to be done slightly differently - using
        # assertAlmostEqual instead.  This may be needed because datetimes are
        # represented as floats under the hood?  Need to check that though.

        in_data = {'x': datetime.now(tz=tz.tzutc())}
        data = to_transit(in_data, protocol)

        response = self.client.post(
            '/echo_transit/' + protocol,
            data=data,
            headers={'content-type': 'application/transit+' + protocol}
        )
        self.assertAlmostEqual(
            from_transit(response.data, protocol)['x'],
            in_data['x'],
            delta=timedelta(milliseconds=10)
        )

    def test_datetime_json(self):
        self._do_datetime_test('json')

    def test_datetime_msgpack(self):
        self._do_datetime_test('msgpack')

    def test_transit_ignores_json(self):
        response = self.client.post(
            '/expect_no_transit',
            data='{"hi": "there"}',
            headers={'content-type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)
