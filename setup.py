from setuptools import setup

setup(name='gdocrevisions',
      version='0.1',
      description='Package for downloading and analyzing google doc revision history data.',
      url='https://github.com/harvard-vpal/gdocrevisions',
      author='Andrew Ang',
      author_email='andrew_ang@harvard.edu',
      license='MIT',
      packages=['gdocrevisions'],
      package_data={'gdocrevisions': ['lib/*', 'bin/*'] },
      zip_safe=False,
)
