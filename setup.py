from setuptools import setup, find_packages
import sys, os

version = '1.0a2'

setup(name='plone.app.workflow',
      version=version,
      description="workflow and security settings for Plone",
      long_description="""\
plone.app.workflow contains workflow- and security-related features for Plone,
including the sharing view.
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Martin Aspeli',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone.app.workflow',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
