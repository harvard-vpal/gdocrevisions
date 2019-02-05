from setuptools import setup

setup(
    name='gdocrevisions',
    version='1.0.1',
    description='Package for downloading and analyzing google doc revision history data.',
    url='https://github.com/harvard-vpal/gdocrevisions',
    author='Andrew Ang',
    author_email='andrew_ang@harvard.edu',
    license='MIT',
    packages=['gdocrevisions'],
    install_requires=[
        'google-auth',
        'google-api-python-client',
        'google-auth-httplib2',  # required for using google.auth credentials with google-api-python-client
        'requests>=2.20.0',
        'future',
    ],
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
)
