import json
from StringIO import StringIO
from datetime import datetime
from flask import Flask, request
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


class FlaskTransitTests(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def _reading_test(self, in_data):
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
