from setuptools import find_packages, setup

requirements = [
    "Click>=7.0",
    "SQLAlchemy>=1.3.12",
    "fastapi>=0.63.0",
    "docker>=4.4.4",
    "passlib>=1.7.4",
    "rich>=9.13.0",
    "numpy>=1.16.5",
    "pandas>=0.24.2",
    "python-dateutil==2.8.1",
    "pytz==2019.3",
    "psycopg2-binary==2.8.6",
    "six==1.14.0",
    "tqdm==4.41.1",
    "pubchempy==1.0.4",
]

setup(
    name="molar",
    packages=find_packages(),
    author=["Theophile Gaudin"],
    version="0.3",
    install_requires=requirements,
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "coverage"],
    extras_require={"doc": ["sphinx_rtd_theme", "nbsphinx", "jupyter"]},
    entry_points=("[console_scripts]\n" "molarcli=molar.cli:cli\n"),
)
