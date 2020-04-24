from setuptools import setup


setup(
    name='flake8-docstrings',
    author='Anna Morozova',
    author_email='morozova2121@yandex.ru',
    version=0.1,
    install_requires=[
        'flake8', 'parso'
    ],
    url='',
    description='Flake8 lint for docstrings.',
    packages=['flake8_docstrings'],
    include_package_data=True,
    entry_points={
        'flake8.extension': [
            'D = flake8_docstrings:DocstringsChecker',
        ],
    },
    license='MIT',
    zip_safe=True,
    keywords='flake8 lint docstrings',
    classifiers=[
        'Environment :: Console',
        'Framework :: Flake8',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ]
)
