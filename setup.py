from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='py_rutracker_client',
  version='0.1.0',
  author='GvozdevAD',
  author_email='alexander@gvozdev.net',
  description='Rutracker Client',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/GvozdevAD/py_rutracker',
  packages=find_packages(),
  install_requires=[
        "beautifulsoup4>=4.12.3",
        "certifi>=2024.8.30",
        "charset-normalizer>=3.3.2",
        "idna>=3.8",
        "lxml>=5.3.0",
        "requests>=2.32.3",
        "soupsieve>=2.6",
        "urllib3>=2.2.2",
        "aiohttp>=3.10.5",
    ],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='rutracker torrent',
  project_urls={
  },
  python_requires='>=3.7'
)