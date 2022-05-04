from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_NAME
from plone.app.workflow.testing import PLONE_APP_WORKFLOW_INTEGRATION_TESTING
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.CMFCore.WorkflowCore import WorkflowException

import unittest


class TestDefaultWorkflow(unittest.TestCase):

    layer = PLONE_APP_WORKFLOW_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        login(self.portal, "manager")

        self.workflow.setChainForPortalTypes(
            ["Document", "News Item"],
            "plone_workflow",
        )

        self.portal.invokeFactory("Document", id="doc")
        self.doc = self.portal.doc

        self.portal.invokeFactory("News Item", id="ni")
        self.ni = self.portal.ni

    def _state(self, obj):
        return self.workflow.getInfoFor(obj, "review_state")

    # Check allowed transitions

    def testOwnerHidesVisibleDocument(self):
        self.assertEqual(self._state(self.doc), "visible")
        self.workflow.doActionFor(self.doc, "hide")
        self.assertEqual(self._state(self.doc), "private")
        self.assertEqual(len(self.catalog(id="doc", review_state="private")), 1)

    def testOwnerShowsPrivateDocument(self):
        self.workflow.doActionFor(self.doc, "hide")
        self.assertEqual(self._state(self.doc), "private")
        self.workflow.doActionFor(self.doc, "show")
        self.assertEqual(self._state(self.doc), "visible")
        self.assertEqual(len(self.catalog(id="doc", review_state="visible")), 1)

    def testOwnerSubmitsVisibleDocument(self):
        self.assertEqual(self._state(self.doc), "visible")
        self.workflow.doActionFor(self.doc, "submit")
        self.assertEqual(self._state(self.doc), "pending")
        self.assertEqual(
            len(self.catalog(id="doc", review_state="pending")),
            1,
        )

    def testOwnerRetractsPendingDocument(self):
        self.workflow.doActionFor(self.doc, "submit")
        self.assertEqual(self._state(self.doc), "pending")
        self.workflow.doActionFor(self.doc, "retract")
        self.assertEqual(self._state(self.doc), "visible")
        self.assertEqual(
            len(self.catalog(id="doc", review_state="visible")),
            1,
        )

    def testOwnerRetractsPublishedDocument(self):
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
        self.assertEqual(self._state(self.doc), "published")
        login(self.portal, "manager")
        self.workflow.doActionFor(self.doc, "retract")
        self.assertEqual(self._state(self.doc), "visible")
        self.assertTrue(
            len(self.catalog(id="doc", review_state="visible")),
            1,
        )

    def testReviewerPublishesPendingDocument(self):
        self.workflow.doActionFor(self.doc, "submit")
        self.assertEqual(self._state(self.doc), "pending")
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
        self.assertEqual(self._state(self.doc), "published")
        self.assertEqual(
            len(self.catalog(id="doc", review_state="published")),
            1,
        )

    def testReviewerRejectsPendingDocument(self):
        self.workflow.doActionFor(self.doc, "submit")
        self.assertEqual(self._state(self.doc), "pending")
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "reject")
        self.assertEqual(self._state(self.doc), "visible")
        self.assertEqual(
            len(self.catalog(id="doc", review_state="visible")),
            1,
        )

    def testReviewerPublishesVisibleDocument(self):
        self.assertEqual(self._state(self.doc), "visible")
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
        self.assertEqual(self._state(self.doc), "published")
        self.assertEqual(
            len(self.catalog(id="doc", review_state="published")),
            1,
        )

    def testReviewerRejectsPublishedDocument(self):
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
        self.assertEqual(self._state(self.doc), "published")
        self.workflow.doActionFor(self.doc, "reject")
        self.assertEqual(self._state(self.doc), "visible")
        self.assertEqual(
            len(self.catalog(id="doc", review_state="visible")),
            1,
        )

    # Check some forbidden transitions

    def testOwnerPublishesVisibleDocument(self):
        self.assertEqual(self._state(self.doc), "visible")
        setRoles(
            self.portal,
            "manager",
            [
                "Owner",
                "Member",
            ],
        )
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.doc,
            "publish",
        )

    def testOwnerSubmitsPrivateDocument(self):
        self.workflow.doActionFor(self.doc, "hide")
        self.assertEqual(self._state(self.doc), "private")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.doc,
            "submit",
        )

    def testManagerPublishesPrivateDocument(self):
        self.workflow.doActionFor(self.doc, "hide")
        self.assertEqual(self._state(self.doc), "private")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.doc,
            "publish",
        )

    # No way am I going to write tests for all impossible transitions ;-)

    # Check view permission

    def testViewVisibleDocument(self):
        # Owner is allowed
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

    def testViewIsNotAcquiredInVisibleState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), "")

    def testViewPrivateDocument(self):
        self.workflow.doActionFor(self.doc, "hide")
        # Owner is allowed
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

    def testViewIsNotAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.doc, "hide")
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), "")

    def testViewPendingDocument(self):
        self.workflow.doActionFor(self.doc, "submit")
        # Owner is allowed
        self.assertTrue(checkPerm(View, self.doc))
        # Member is allowed (TODO:?)
        login(self.portal, "member")
        self.assertTrue(checkPerm(View, self.doc))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(View, self.doc))
        # Anonymous is allowed (TODO:?)
        logout()
        self.assertTrue(checkPerm(View, self.doc))

    def testViewIsNotAcquiredInPendingState(self):
        self.workflow.doActionFor(self.doc, "submit")
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), "")

    def testViewPublishedDocument(self):
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
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

    def testViewIsNotAcquiredInPublishedState(self):
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), "")

    # Check access contents info permission

    def testAccessVisibleDocument(self):
        # Owner is allowed
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

    def testAccessContentsInformationIsNotAcquiredInVisibleState(self):
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(AccessContentsInformation),
            "",
        )

    def testAccessPrivateDocument(self):
        self.workflow.doActionFor(self.doc, "hide")
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

    def testAccessContentsInformationIsNotAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.doc, "hide")
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(AccessContentsInformation),
            "",
        )

    def testAccessPendingDocument(self):
        self.workflow.doActionFor(self.doc, "submit")
        # Owner is allowed
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Member is allowed (TODO:?)
        login(self.portal, "member")
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Anonymous is allowed (TODO:?)
        logout()
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))

    def testAccessContentsInformationIsNotAcquiredInPendingState(self):
        self.workflow.doActionFor(self.doc, "submit")
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(AccessContentsInformation),
            "",
        )

    def testAccessPublishedDocument(self):
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
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

    def testAccessContentsInformationIsNotAcquiredInPublishedState(self):
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(AccessContentsInformation),
            "",
        )

    # Check modify content permissions

    def testModifyVisibleDocument(self):
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

    def testModifyPortalContentIsNotAcquiredInVisibleState(self):
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(ModifyPortalContent),
            "",
        )

    def testModifyPrivateDocument(self):
        self.workflow.doActionFor(self.doc, "hide")
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

    def testModifyPortalContentIsNotAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.doc, "hide")
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(ModifyPortalContent),
            "",
        )

    def testModifyPendingDocument(self):
        self.workflow.doActionFor(self.doc, "submit")
        # Owner is denied
        setRoles(
            self.portal,
            "manager",
            [
                "Owner",
                "Member",
            ],
        )
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(ModifyPortalContent, self.doc))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))

    def testModifyPortalContentIsNotAcquiredInPendingState(self):
        self.workflow.doActionFor(self.doc, "submit")
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(ModifyPortalContent),
            "",
        )

    def testModifyPublishedDocument(self):
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
        # Owner is denied
        login(self.portal, TEST_USER_NAME)
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))

    def testModifyPortalContentIsNotAcquiredInPublishedState(self):
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
        self.assertEqual(
            self.doc.acquiredRolesAreUsedBy(ModifyPortalContent),
            "",
        )

    # Check catalog search

    def testFindVisibleDocument(self):
        # Owner is allowed
        self.assertTrue(self.catalog(id="doc"))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(self.catalog(id="doc"))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(self.catalog(id="doc"))
        # Anonymous is allowed
        logout()
        self.assertTrue(self.catalog(id="doc"))

    def testFindPrivateDocument(self):
        self.workflow.doActionFor(self.doc, "hide")
        # Owner is allowed
        self.assertTrue(self.catalog(id="doc"))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(self.catalog(id="doc"))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(self.catalog(id="doc"))
        # Anonymous is denied
        logout()
        self.assertFalse(self.catalog(id="doc"))

    def testFindPendingDocument(self):
        self.workflow.doActionFor(self.doc, "submit")
        # Owner is allowed
        self.assertTrue(self.catalog(id="doc"))
        # Member is allowed (TODO:?)
        login(self.portal, "member")
        self.assertTrue(self.catalog(id="doc"))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(self.catalog(id="doc"))
        # Anonymous is allowed (TODO:?)
        logout()
        self.assertTrue(self.catalog(id="doc"))

    def testFindPublishedDocument(self):
        login(self.portal, "reviewer")
        self.workflow.doActionFor(self.doc, "publish")
        # Owner is allowed
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(self.catalog(id="doc"))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(self.catalog(id="doc"))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(self.catalog(id="doc"))
        # Anonymous is allowed
        logout()
        self.assertTrue(self.catalog(id="doc"))

    def testMyWorklist(self):
        # When a member has the local Reviewer role, pending
        # docs should show up in his worklist.
        self.workflow.doActionFor(self.doc, "submit")
        self.doc.manage_addLocalRoles("member", ["Reviewer"])
        login(self.portal, "reviewer")
        worklist = self.portal.portal_workflow.getWorklistsResults()
        self.assertTrue(len(worklist) == 1)
        self.assertTrue(worklist[0] == self.doc)
        login(self.portal, "member")
        worklist = self.portal.portal_workflow.getWorklistsResults()
        self.assertTrue(len(worklist) == 1)
        self.assertTrue(worklist[0] == self.doc)

    def testStateTitles(self):
        state_titles = {
            "private": "Private",
            "visible": "Public draft",
            "pending": "Pending review",
            "published": "Published",
        }

        wf = self.workflow.plone_workflow

        for state_id, title in state_titles.items():
            state = getattr(wf.states, state_id, None)
            if state is not None:
                self.assertEqual(state.title, title)
