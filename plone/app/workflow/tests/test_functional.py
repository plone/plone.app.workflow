from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.workflow.testing import optionflags
from plone.app.workflow.testing import PLONE_APP_WORKFLOW_FUNCTIONAL_TESTING
from plone.testing import layered
from Products.CMFCore.utils import getToolByName

import doctest
import re
import transaction
import unittest


doctests = (
    "onestateworkflow.rst",
    "sharingpage.rst",
)


def setup(doctest):

    portal = doctest.globs["layer"]["portal"]
    login(portal, "member")
    setRoles(
        portal,
        "member",
        [
            "Manager",
        ],
    )
    workflow = getToolByName(portal, "portal_workflow")
    workflow.setChainForPortalTypes(
        (
            "Folder",
            "Document",
            "News Item",
            "Event",
        ),
        ("one_state_workflow",),
    )
    portal.invokeFactory("Folder", "folder1")
    folder = portal.folder1
    folder.invokeFactory("Document", "document1")
    folder.invokeFactory("News Item", "newsitem1")
    setRoles(
        portal,
        "member",
        [
            "Member",
        ],
    )
    logout()
    transaction.commit()


def test_suite():
    suite = unittest.TestSuite()
    tests = [
        layered(
            doctest.DocFileSuite(
                f"tests/{test_file}",
                package="plone.app.workflow",
                optionflags=optionflags,
                setUp=setup,
            ),
            layer=PLONE_APP_WORKFLOW_FUNCTIONAL_TESTING,
        )
        for test_file in doctests
    ]
    suite.addTests(tests)
    return suite
