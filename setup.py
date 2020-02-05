from setuptools import setup, find_packages

requirements = [
    "certifi==2019.11.28",
    "numpy==1.18.1",
    "pandas==0.25.3",
    "psycopg2-binary==2.8.4",
    "python-dateutil==2.8.1",
    "pytz==2019.3",
    "six==1.14.0",
    "SQLAlchemy==1.3.12",
    "tqdm==4.41.1",
    "paramiko==2.7.1",
    "coloredlogs==10.0",
]

setup(
    name='mdb',
    packages=find_packages(),
    author=['Theophile Gaudin'],
    install_requires=requirements,
    setup_requires=["pytest-runner"],
    tests_require=['pytest', 'coverage'],
    extras_require={'doc': ['sphinx_rtd_theme',
                            'nbsphinx',
                            'jupyter']},
)
