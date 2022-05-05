from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.workflow.testing import PLONE_APP_WORKFLOW_INTEGRATION_TESTING
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.CMFCore.WorkflowCore import WorkflowException

import unittest


class TestFolderWorkflow(unittest.TestCase):

    layer = PLONE_APP_WORKFLOW_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        login(self.portal, "manager")
        self.workflow.setChainForPortalTypes(["Folder"], "folder_workflow")

        self.portal.invokeFactory("Folder", id="dir")
        self.dir = self.portal.dir

        setRoles(
            self.portal,
            "manager",
            [
                "Owner",
                "Member",
            ],
        )

    def _state(self, obj):
        return self.workflow.getInfoFor(obj, "review_state")

    # Check allowed transitions

    def testOwnerHidesVisibleFolder(self):
        self.assertEqual(self._state(self.dir), "visible")
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self._state(self.dir), "private")
        self.assertTrue(self.catalog(id="dir", review_state="private"))

    def testOwnerShowsPrivateFolder(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self._state(self.dir), "private")
        self.workflow.doActionFor(self.dir, "show")
        self.assertEqual(self._state(self.dir), "visible")
        self.assertTrue(self.catalog(id="dir", review_state="visible"))

    def testOwnerPublishesPrivateFolder(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self._state(self.dir), "private")
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        self.assertTrue(self.catalog(id="dir", review_state="published"))

    def testOwnerPublishesVisibleFolder(self):
        self.assertEqual(self._state(self.dir), "visible")
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        self.assertTrue(self.catalog(id="dir", review_state="published"))

    def testOwnerHidesPublishedFolder(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self._state(self.dir), "private")
        self.assertTrue(self.catalog(id="dir", review_state="private"))

    def testOwnerRetractsPublishedFolder(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        self.workflow.doActionFor(self.dir, "retract")
        self.assertEqual(self._state(self.dir), "visible")
        self.assertTrue(self.catalog(id="dir", review_state="visible"))

    def testManagerPublishesVisibleFolder(self):
        self.assertEqual(self._state(self.dir), "visible")
        login(self.portal, "manager")
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        self.assertTrue(self.catalog(id="dir", review_state="published"))

    def testManagerPublishesPrivateFolder(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self._state(self.dir), "private")
        login(self.portal, "manager")
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        self.assertTrue(self.catalog(id="dir", review_state="published"))

    def testManagerRetractsPublishedFolder(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        login(self.portal, "manager")
        self.workflow.doActionFor(self.dir, "retract")
        self.assertEqual(self._state(self.dir), "visible")
        self.assertTrue(self.catalog(id="dir", review_state="visible"))

    # Check forbidden transitions

    def testMemberHidesVisibleFolder(self):
        self.assertEqual(self._state(self.dir), "visible")
        login(self.portal, "member")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "hide",
        )

    def testMemberShowsPrivateFolder(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self._state(self.dir), "private")
        login(self.portal, "member")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "show",
        )

    def testMemberPublishesVisibleFolder(self):
        self.assertEqual(self._state(self.dir), "visible")
        login(self.portal, "member")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "publish",
        )

    def testMemberPublishesPrivateFolder(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self._state(self.dir), "private")
        login(self.portal, "member")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "publish",
        )

    def testMemberHidesPublishedFolder(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        login(self.portal, "member")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "hide",
        )

    def testMemberRetractsPublishedFolder(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        login(self.portal, "member")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "retract",
        )

    def testReviewerHidesVisibleFolder(self):
        self.assertEqual(self._state(self.dir), "visible")
        login(self.portal, "reviewer")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "hide",
        )

    def testReviewerShowsPrivateFolder(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self._state(self.dir), "private")
        login(self.portal, "reviewer")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "show",
        )

    def testReviewerPublishesVisibleFolder(self):
        self.assertEqual(self._state(self.dir), "visible")
        login(self.portal, "reviewer")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "publish",
        )

    def testReviewerPublishesPrivateFolder(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self._state(self.dir), "private")
        login(self.portal, "reviewer")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "publish",
        )

    def testReviewerHidesPublishedFolder(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        login(self.portal, "reviewer")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "hide",
        )

    def testReviewerRetractsPublishedFolder(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        login(self.portal, "reviewer")
        self.assertRaises(
            WorkflowException,
            self.workflow.doActionFor,
            self.dir,
            "retract",
        )

    def testManagerHidesVisibleFolder(self):
        self.assertEqual(self._state(self.dir), "visible")
        login(self.portal, "manager")
        self.workflow.doActionFor(self.dir, "hide")

    def testManagerShowsPrivateFolder(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self._state(self.dir), "private")
        login(self.portal, "manager")
        self.workflow.doActionFor(self.dir, "show")

    def testManagerHidesPublishedFolder(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self._state(self.dir), "published")
        login(self.portal, "manager")
        self.workflow.doActionFor(self.dir, "hide")

    # Check view permissions

    def testViewVisibleFolder(self):
        # Owner is allowed
        self.assertTrue(checkPerm(View, self.dir))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(checkPerm(View, self.dir))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(View, self.dir))
        # Anonymous is allowed
        logout()
        self.assertTrue(checkPerm(View, self.dir))

    def testViewIsNotAcquiredInVisibleState(self):
        self.assertEqual(self.dir.acquiredRolesAreUsedBy(View), "")

    def testViewPrivateFolder(self):
        self.workflow.doActionFor(self.dir, "hide")
        # Owner is allowed
        self.assertTrue(checkPerm(View, self.dir))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(View, self.dir))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(checkPerm(View, self.dir))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(View, self.dir))

    def testViewIsNotAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(self.dir.acquiredRolesAreUsedBy(View), "")

    def testViewPublishedFolder(self):
        self.workflow.doActionFor(self.dir, "publish")
        # Owner is allowed
        self.assertTrue(checkPerm(View, self.dir))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(checkPerm(View, self.dir))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(View, self.dir))
        # Anonymous is allowed
        logout()
        self.assertTrue(checkPerm(View, self.dir))

    def testViewIsNotAcquiredInPublishedState(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(self.dir.acquiredRolesAreUsedBy(View), "")

    # Check access contents info permission

    def testAccessVisibleFolderContents(self):
        # Owner is allowed
        self.assertTrue(checkPerm(AccessContentsInformation, self.dir))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(checkPerm(AccessContentsInformation, self.dir))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(AccessContentsInformation, self.dir))
        # Anonymous is allowed
        logout()
        self.assertTrue(checkPerm(AccessContentsInformation, self.dir))

    def testAccessContentsInformationIsNotAcquiredInVisibleState(self):
        self.assertEqual(
            self.dir.acquiredRolesAreUsedBy(AccessContentsInformation),
            "",
        )

    def testAccessPrivateFolderContents(self):
        self.workflow.doActionFor(self.dir, "hide")
        # Owner is allowed
        self.assertTrue(checkPerm(AccessContentsInformation, self.dir))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(AccessContentsInformation, self.dir))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(checkPerm(AccessContentsInformation, self.dir))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(AccessContentsInformation, self.dir))

    def testAccessContentsInformationIsNotAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(
            self.dir.acquiredRolesAreUsedBy(AccessContentsInformation),
            "",
        )

    def testAccessPublishedFolderContents(self):
        self.workflow.doActionFor(self.dir, "publish")
        # Owner is allowed
        self.assertTrue(checkPerm(AccessContentsInformation, self.dir))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(checkPerm(AccessContentsInformation, self.dir))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(AccessContentsInformation, self.dir))
        # Anonymous is allowed
        logout()
        self.assertTrue(checkPerm(AccessContentsInformation, self.dir))

    def testAccessContentsInformationIsNotAcquiredInPublishedState(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(
            self.dir.acquiredRolesAreUsedBy(AccessContentsInformation),
            "",
        )

    # Check modify contents permission

    def testModifyVisibleFolderContents(self):
        # Owner is allowed
        self.assertTrue(checkPerm(ModifyPortalContent, self.dir))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(ModifyPortalContent, self.dir))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(checkPerm(ModifyPortalContent, self.dir))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(ModifyPortalContent, self.dir))

    def testModifyPortalContentIsNotAcquiredInVisibleState(self):
        self.assertEqual(
            self.dir.acquiredRolesAreUsedBy(ModifyPortalContent),
            "",
        )

    def testModifyPrivateFolderContents(self):
        self.workflow.doActionFor(self.dir, "hide")
        # Owner is allowed
        self.assertTrue(checkPerm(ModifyPortalContent, self.dir))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(ModifyPortalContent, self.dir))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(checkPerm(ModifyPortalContent, self.dir))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(ModifyPortalContent, self.dir))

    def testModifyPortalContentIsNotAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(
            self.dir.acquiredRolesAreUsedBy(ModifyPortalContent),
            "",
        )

    def testModifyPublishedFolderContents(self):
        self.workflow.doActionFor(self.dir, "publish")
        # Owner is allowed
        self.assertTrue(checkPerm(ModifyPortalContent, self.dir))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(ModifyPortalContent, self.dir))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(checkPerm(ModifyPortalContent, self.dir))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(ModifyPortalContent, self.dir))

    def testModifyPortalContentIsNotAcquiredInPublishedState(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(
            self.dir.acquiredRolesAreUsedBy(ModifyPortalContent),
            "",
        )

    # Check list contents permission

    def testListVisibleFolderContents(self):
        # Owner is allowed
        self.assertTrue(checkPerm(ListFolderContents, self.dir))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(ListFolderContents, self.dir))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(ListFolderContents, self.dir))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(ListFolderContents, self.dir))

    def testListFolderContentsIsAcquiredInVisibleState(self):
        self.assertEqual(
            self.dir.acquiredRolesAreUsedBy(ListFolderContents),
            "CHECKED",
        )

    def testListPrivateFolderContents(self):
        self.workflow.doActionFor(self.dir, "hide")
        # Owner is allowed
        self.assertTrue(checkPerm(ListFolderContents, self.dir))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(ListFolderContents, self.dir))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(ListFolderContents, self.dir))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(ListFolderContents, self.dir))

    def testListFolderContentsIsAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.dir, "hide")
        self.assertEqual(
            self.dir.acquiredRolesAreUsedBy(ListFolderContents),
            "CHECKED",
        )

    def testListPublishedFolderContents(self):
        self.workflow.doActionFor(self.dir, "publish")
        # Owner is allowed
        self.assertTrue(checkPerm(ListFolderContents, self.dir))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(checkPerm(ListFolderContents, self.dir))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(checkPerm(ListFolderContents, self.dir))
        # Anonymous is denied
        logout()
        self.assertFalse(checkPerm(ListFolderContents, self.dir))

    def testListFolderContentsNotAcquiredInPublishedState(self):
        self.workflow.doActionFor(self.dir, "publish")
        self.assertEqual(
            self.dir.acquiredRolesAreUsedBy(ListFolderContents),
            "CHECKED",
        )

    # Check catalog search

    def testFindVisibleFolder(self):
        # Owner is allowed
        self.assertTrue(self.catalog(id="dir"))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(self.catalog(id="dir"))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(self.catalog(id="dir"))
        # Anonymous is allowed
        logout()
        self.assertTrue(self.catalog(id="dir"))

    def testFindPrivateFolder(self):
        self.workflow.doActionFor(self.dir, "hide")
        # Owner is allowed
        self.assertTrue(self.catalog(id="dir"))
        # Member is denied
        login(self.portal, "member")
        self.assertFalse(self.catalog(id="dir"))
        # Reviewer is denied
        login(self.portal, "reviewer")
        self.assertFalse(self.catalog(id="dir"))
        # Anonymous is denied
        logout()
        self.assertFalse(self.catalog(id="dir"))

    def testFindPublishedFolder(self):
        self.workflow.doActionFor(self.dir, "publish")
        # Owner is allowed
        self.assertTrue(self.catalog(id="dir"))
        # Member is allowed
        login(self.portal, "member")
        self.assertTrue(self.catalog(id="dir"))
        # Reviewer is allowed
        login(self.portal, "reviewer")
        self.assertTrue(self.catalog(id="dir"))
        # Anonymous is allowed
        logout()
        self.assertTrue(self.catalog(id="dir"))
