from setuptools import setup, find_packages

setup(
    name='space-env',
    version='0.1.dev0',
    description='An environment for simulated space flying tasks',
    url='https://github.com/galleon/space-env',
    author='Guillaume Alleon',
    author_email='guillaume.alleon@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Researchers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',

        'Programming Language :: Python :: 3.7',
    ],

    keywords='autonomous flying simulation environment reinforcement learning',
    packages=find_packages(exclude=['docs', 'scripts', 'tests']),
    install_requires=['gym', 'jax', 'pygame', 'matplotlib'],
    tests_require=['pytest'],
    extras_require={
        'dev': ['scipy'],
        'deploy': ['pytest-runner', 'sphinx<1.7.3', 'sphinx_rtd_theme']
    },
    entry_points={
        'console_scripts': [],
    },
)