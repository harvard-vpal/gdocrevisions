from setuptools import setup

setup(name='gdocrevisions',
      version='0.3',
      description='Package for downloading and analyzing google doc revision history data.',
      url='https://github.com/harvard-vpal/gdocrevisions',
      author='Andrew Ang',
      author_email='andrew_ang@harvard.edu',
      license='MIT',
      packages=['gdocrevisions'],
      install_requires=[
      	'oauth2client',
      	'google-api-python-client',
      ],
)
