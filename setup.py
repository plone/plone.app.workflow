from setuptools import setup, find_packages

version = '2.0.8'

setup(name='plone.app.workflow',
      version=version,
      description="workflow and security settings for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
        ],
      keywords='',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.workflow',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'Products.CMFCalendar',
            'Products.PloneTestCase',
        ]
      ),
      install_requires=[
        'setuptools',
        'kss.core',
        'plone.app.kss',
        'plone.memoize',
        'transaction',
        'zope.component',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        'zope.site',
        'zope.testing',
        'Acquisition',
        'DateTime',
        'Products.CMFPlone',
        'Products.CMFCore',
        'Products.DCWorkflow',
        'Products.GenericSetup',
        'Products.statusmessages',
        'Zope2',
      ],
      )
