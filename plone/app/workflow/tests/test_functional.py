# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.workflow.testing import PLONE_APP_WORKFLOW_FUNCTIONAL_TESTING
from plone.app.workflow.testing import optionflags
from plone.testing import layered
from Products.CMFCore.utils import getToolByName

import doctest
import re
import six
import transaction
import unittest


doctests = (
    'onestateworkflow.rst',
    'sharingpage.rst',
)


def setup(doctest):

    portal = doctest.globs['layer']['portal']
    login(portal, 'member')
    setRoles(portal, 'member', ['Manager', ])
    workflow = getToolByName(portal, 'portal_workflow')
    workflow.setChainForPortalTypes(
        ('Folder', 'Document', 'News Item', 'Event', ),
        ('one_state_workflow', ),
    )
    portal.invokeFactory('Folder', 'folder1')
    folder = portal.folder1
    folder.invokeFactory('Document', 'document1')
    folder.invokeFactory('News Item', 'newsitem1')
    setRoles(portal, 'member', ['Member', ])
    logout()
    transaction.commit()


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if six.PY2:
            want = re.sub('zope.testbrowser.browser.LinkNotFoundError', 'LinkNotFoundError', want)  # noqa: E501
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    suite = unittest.TestSuite()
    tests = [
        layered(
            doctest.DocFileSuite(
                'tests/{0}'.format(test_file),
                package='plone.app.workflow',
                optionflags=optionflags,
                setUp=setup,
                checker=Py23DocChecker(),
            ),
            layer=PLONE_APP_WORKFLOW_FUNCTIONAL_TESTING,
        )
        for test_file in doctests
    ]
    suite.addTests(tests)
    return suite

