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
