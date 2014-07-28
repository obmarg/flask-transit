import json
from dateutil import tz
from StringIO import StringIO
from datetime import datetime
from flask import Flask, request, abort
from flask.ext.transit import init_transit
from flask.ext.testing import TestCase
from transit.writer import Writer
from transit.reader import Reader

app = Flask('tests')
init_transit(app)


def to_transit(in_data):
    io = StringIO()
    writer = Writer(io, 'json')
    writer.write(in_data)
    return io.getvalue()


def from_transit(in_data):
    io = StringIO(in_data)
    return Reader().read(io)


@app.route('/echo_transit', methods=['POST'])
def echo_transit():
    return to_transit(request.transit)

@app.route('/expect_no_transit', methods=['POST'])
def expect_no_transit():
    if request.transit:
        abort(400)
    return 'ok'


class FlaskTransitTests(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def _reading_test(self, in_data):
        # TODO: Need to test msgpack as well as json
        data = to_transit(in_data)

        response = self.client.post(
            '/echo_transit',
            data=data,
            headers={'content-type': 'application/transit+json'}
        )

        self.assertEqual(response.data, data)
        self.assertEqual(from_transit(response.data), in_data)

    def test_basic_transit_reading(self):
        self._reading_test({'hi': 'there',
                            'ls': (1, 2, 3),
                            'aset': frozenset({1, 2, 3})})

    def test_transit_datetime_reading(self):
        # TODO: Could change this to use almostEqual instead, since
        #       I reckon it's a floating point related failure.
        self._reading_test({'date': datetime.now(tz.tzutc())})

    def test_transit_ignores_json(self):
        response = self.client.post(
            '/expect_no_transit',
            data='{"hi": "there"}',
            headers={'content-type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)
