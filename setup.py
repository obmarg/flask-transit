"""
Flask-Transit
-------------

Flask-transit is a Flask_ extension to make working with Transit_ easier.

.. _Flask: http://flask.pocoo.org/
.. _Transit: https://github.com/cognitect/transit-python
"""
from setuptools import setup


setup(
    name='Flask-Transit',
    version='0.1.0-pre',
    url='http://github.com/obmarg/flask-transit',
    license='BSD',
    author='Graeme Coupar',
    author_email='grambo@grambo.me.uk',
    description='A flask extension for working with transit data.',
    long_description=__doc__,
    py_modules=['flask_transit'],
    zip_safe=False,
    include_package_data=False,
    platforms='any',
    install_requires=[
        'Flask',
        'transit-python'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        'Development Status :: 4 - Beta',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
