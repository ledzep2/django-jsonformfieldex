from setuptools import setup

setup(name='django-jsonformfieldex',
      version='0.9',
      author='Russell',
      author_email='yufeiwu@gmail.com',
      packages=['jsonformfieldex'],
      requires=['django'],
      license='MIT',
      long_description="A django form field that renders a value dict as a grouped and typed fields.")
