from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_NAME
from plone.app.workflow.testing import PLONE_APP_WORKFLOW_INTEGRATION_TESTING
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _checkPermission as checkPerm

import unittest


class TestOneStateWorkflow(unittest.TestCase):

    layer = PLONE_APP_WORKFLOW_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        login(self.portal, "manager")

        self.workflow.setChainForPortalTypes(
            ["Document", "News Item"], "one_state_workflow"
        )

        self.portal.invokeFactory("Document", id="doc")
        self.doc = self.portal.doc
        self.portal.invokeFactory("News Item", id="ni")
        self.ni = self.portal.ni

    def _state(self, obj):
        return self.workflow.getInfoFor(obj, "review_state")

    # Check allowed transitions: none for one state workflow

    def testInitialState(self):
        self.assertEqual(self._state(self.doc), "published")
        self.assertEqual(self._state(self.ni), "published")

    # Check view permission

    def testViewIsNotAcquiredInPublishedState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), "")  # not checked

    def testViewPublishedDocument(self):
        # Owner is allowed
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(checkPerm(View, self.doc))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(checkPerm(View, self.doc))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(View, self.doc))
        # Anonymous is allowed
        logout()
        self.assertTrue(checkPerm(View, self.doc))
        # Editor is allowed
        login(self.portal, "editor")
        self.assertTrue(checkPerm(View, self.doc))
        # Reader is allowed
        login(self.portal, "reader")
        self.assertTrue(checkPerm(View, self.doc))

    # Check access contents info permission

    def testAccessContentsInformationIsNotAcquiredInPublishedState(self):
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(AccessContentsInformation), ""
        )  # not checked

    def testAccessPublishedDocument(self):
        # Owner is allowed
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Anonymous is allowed
        logout()
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Editor is allowed
        login(self.portal, "editor")
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Reader is allowed
        login(self.portal, "reader")
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))

    def testModifyPortalContentIsNotAcquiredInPublishedState(self):
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(ModifyPortalContent),
            "",
        )

    def testModifyPublishedDocument(self):
        # Owner is allowed
        setRoles(
            self.portal,
            "manager",
            [
                "Owner",
                "Member",
            ],
        )
        self.assertTrue(checkPerm(ModifyPortalContent, self.doc))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Editor is allowed
        login(self.portal, "editor")
        self.assertTrue(checkPerm(ModifyPortalContent, self.doc))
        # Reader is denied
        login(self.portal, "reader")
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))

    # Check change events permission

    def testChangeEventsIsNotAcquiredInPublishedState(self):
        # since r104169 event content doesn't use `ChangeEvents` anymore...
        self.assertEqual(
            self.ni.acquiredRolesAreUsedBy(ModifyPortalContent),
            "",
        )
