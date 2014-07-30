flask-transit
------

Flask-transit is a [flask](http://flask.pocoo.org/) extension to make working
with
[transit](https://github.com/cognitect/transit-python) easier.

### Installation

Flask-transit can be installed by running:

    pip install --use-wheel --pre flask-transi

### Use

Flask-transit must be initialized by calling `init_transit`, passing in the
flask application you wish to use with transit.  For example:

    from flask import Flask
    from flask.ext.transit import init_transit

    app = Flask(__name__)
    init_transit(app)

Then, if you wish to return a response encoded in transit from an endpoint, you
can use the transition function:

    @app.route('/gimme_transit')
    def gimme_transit():
        return transition({'pizza': 'tasty',
                           'pasta': 'tasty'})

If an endpoint receives data encoded in Transit, it will be avalaible on the
`request.transit` property:

    @app.route('/read_transit', methods=['POST'])
    def read_transit():
        data = request.transit
        return data['pizza']

Data to be read by flask-transit should be encoded with a transit MIME type.
