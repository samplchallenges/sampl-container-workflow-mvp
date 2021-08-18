from setuptools import setup

setup(
    name='AutoDock-rdkit-eg',
    version='0.1',
    py_modules=[
		'autodock',
		'run_autodock',
	],
    install_requires=[
        'Click',
	'mdtraj',
    ],
    entry_points='''
        [console_scripts]
        run-autodock=run_autodock:run_autodock
    ''',
)
