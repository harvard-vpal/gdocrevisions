from setuptools import setup

setup(
    name='gdocrevisions',
    version='0.5.1',
    description='Package for downloading and analyzing google doc revision history data.',
    url='https://github.com/harvard-vpal/gdocrevisions',
    author='Andrew Ang',
    author_email='andrew_ang@harvard.edu',
    license='MIT',
    packages=['gdocrevisions'],
    install_requires=[
        'google-auth==1.4.1',
        'google-api-python-client==1.6.6',
        'google-auth-httplib2==0.0.3',  # required for using google.auth credentials with google-api-python-client
        'requests==2.18.1',
        'future==0.16.0',
    ],
)
