from plone.app.testing import login
from plone.app.testing import logout
from plone.app.workflow.testing import PLONE_APP_WORKFLOW_INTEGRATION_TESTING
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.CMFCore.WorkflowCore import WorkflowException

import unittest


SIMPLE = "simple_publication_workflow"


class TestSimplePublicationWorkflow(unittest.TestCase):

    layer = PLONE_APP_WORKFLOW_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        login(self.portal, "manager")

        self._set_workflow_for_portal_type(SIMPLE, "Document")
        self.portal.invokeFactory("Document", "document1")
        self.doc = self.portal.document1

    def _set_workflow_for_portal_type(self, workflow_name, portal_type):
        self.workflow.setChainForPortalTypes(
            (portal_type,),
            (workflow_name,),
        )

    def _check_state(self, obj, expected_review_state):
        current_state = self.workflow.getInfoFor(obj, "review_state")
        self.assertEqual(
            current_state,
            expected_review_state,
            "Object {} should have review state {} but has {}".format(
                obj,
                expected_review_state,
                current_state,
            ),
        )

    # Check allowed transitions: two for simple publication workflow

    def testOwnerSubmitAPrivateDocumentAndRetract(self):
        self._check_state(self.doc, "private")
        self.workflow.doActionFor(self.doc, "submit")
        self._check_state(self.doc, "pending")
        self.workflow.doActionFor(self.doc, "retract")
        self._check_state(self.doc, "private")

    # Check some forbidden transitions

    def testOwnerCannotPublishDocument(self):
        login(self.portal, "member")
        self._check_state(self.doc, "private")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.doc,
            "publish",
        )

    # Check view permission

    def testViewIsNotAcquiredInPrivateState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), "")  # not checked

    def testViewPrivateDocument(self):
        self._check_state(self.doc, "private")
        # Owner is allowed
        login(self.portal, "manager")
        self.assertTrue(checkPerm(View, self.doc))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(View, self.doc))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(checkPerm(View, self.doc))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(View, self.doc))
        # Editor is allowed
        login(self.portal, "editor")
        self.assertTrue(checkPerm(View, self.doc))
        # Reader is allowed
        login(self.portal, "reader")
        self.assertTrue(checkPerm(View, self.doc))

    def testViewIsNotAcquiredInPublishedState(self):
        # transition requires Review portal content
        login(self.portal, "manager")
        self.workflow.doActionFor(self.doc, "publish")
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), "")  # not checked

    def testViewPublishedDocument(self):
        # transition requires Review portal content
        login(self.portal, "manager")
        self.workflow.doActionFor(self.doc, "publish")
        # Owner is allowed
        self.assertTrue(checkPerm(View, self.doc))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(checkPerm(View, self.doc))
        # Reviewer is denied  but he acquires through Anonymous Role
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

    def testAccessContentsInformationIsNotAcquiredInPrivateState(self):
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(AccessContentsInformation), ""
        )  # not checked

    def testAccessContentsInformationPrivateDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, "review_state"), "private")
        # Owner is allowed
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(checkPerm(AccessContentsInformation, self.doc))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(AccessContentsInformation, self.doc))
        # Editor is allowed
        login(self.portal, "editor")
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Reader is allowed
        login(self.portal, "reader")
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))

    def testAccessContentsInformationIsNotAcquiredInPublishedState(self):
        # transition requires Review portal content
        self.workflow.doActionFor(self.doc, "publish")
        # not checked
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(AccessContentsInformation),
            "",
        )

    def testAccessContentsInformationPublishedDocument(self):
        # transition requires Review portal content
        self.workflow.doActionFor(self.doc, "publish")
        # Owner is allowed
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is denied but he acquires through Anonymous Role
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

    # Check modify content permissions

    def testModifyPrivateDocumentIsNotAcquiredInPrivateState(self):
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(ModifyPortalContent), ""
        )  # not checked

    def testModifyPrivateDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, "review_state"), "private")
        # Owner is allowed
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

    def testModifyPortalContentIsNotAcquiredInPublishedState(self):
        # transition requires Review portal content
        self.workflow.doActionFor(self.doc, "publish")
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(ModifyPortalContent), "")

    def testModifyPublishedDocument(self):
        # transition requires Review portal content
        self.workflow.doActionFor(self.doc, "publish")
        # Manager is allowed
        self.assertTrue(checkPerm(ModifyPortalContent, self.doc))
        # Owner is allowed
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
