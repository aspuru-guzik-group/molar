from setuptools import setup, find_packages

requirements = [
    "certifi==2019.6.16",
    "numpy==1.16.4",
    "pandas==0.24.2",
    "psycopg2-binary==2.8.3",
    "python-dateutil==2.8.0",
    "pytz==2019.1",
    "six==1.12.0",
    "SQLAlchemy==1.3.5",
]

setup(
    name='goldmine',
    packages=find_packages(),
    author=['Theophile Gaudin'],
    install_requires=requirements,
    setup_requires=["pytest-runner"],
    tests_require=['pytest'],
    extras_require={'doc': ['sphinx_rtd_theme',
                            'nbsphinx',
                            'jupyter']},
)
