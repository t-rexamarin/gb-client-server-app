from setuptools import setup, find_packages

setup(name="mess_client_proj_roma_june",
      version="0.0.1",
      description="mess_server_proj",
      author="Roman Khoroshev",
      author_email="zizigi@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
