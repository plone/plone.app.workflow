from unittest import TestSuite
from utils import optionflags
from Testing.ZopeTestCase import ZopeDocFileSuite
from base import WorkflowTestCase


def test_suite():
    tests = ['onestateworkflow.rst', 'sharingpage.rst']
    suite = TestSuite()
    for test in tests:
        suite.addTest(ZopeDocFileSuite(test,
            optionflags=optionflags,
            package="plone.app.workflow.tests",
            test_class=WorkflowTestCase))
    return suite
