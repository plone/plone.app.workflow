from setuptools import setup, find_packages

version = '5.0.0a2'

setup(
    name='plone.app.workflow',
    version=version,
    description="workflow and security settings for Plone",
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGES.rst").read()),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords='workflow sharing plone',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.org/project/plone.app.workflow',
    license='GPL version 2',
    packages=find_packages(),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'plone.app.testing',
        ]
    ),
    install_requires=[
        'setuptools',
        'plone.memoize',
        'six',
        'transaction',
        'zope.component',
        'zope.dottedname',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.schema',
        'zope.site',
        'zope.testing',
        'Acquisition',
        'DateTime',
        'Products.CMFCore>=2.4.0',
        'Products.DCWorkflow',
        'Products.GenericSetup >= 2.0',
        'Products.statusmessages',
        'Zope2',
    ],
)
