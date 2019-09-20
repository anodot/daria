from setuptools import setup, find_packages

setup(
    name='agent',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points='''
        [console_scripts]
        agent=agent.cli:agent
    ''',
    zip_safe=False
)
