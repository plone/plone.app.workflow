from base import WorkflowTestCase
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
ChangeEvents = 'Change portal events'


class TestOneStateWorkflow(WorkflowTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.workflow.setChainForPortalTypes(['Document', 'News Item'], 'one_state_workflow')

        self.portal.acl_users._doAddUser('member', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('reviewer', 'secret', ['Reviewer'], [])
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.portal.acl_users._doAddUser('editor', ' secret', ['Editor'], [])
        self.portal.acl_users._doAddUser('reader', 'secret', ['Reader'], [])

        self.folder.invokeFactory('Document', id='doc')
        self.doc = self.folder.doc
        self.folder.invokeFactory('News Item', id='ni')
        self.ni = self.folder.ni

    # Check allowed transitions: none for one state workflow

    def testInitialState(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'published')
        self.assertEqual(self.workflow.getInfoFor(self.ni, 'review_state'), 'published')

    # Check view permission

    def testViewIsNotAcquiredInPublishedState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), '')   # not checked

    def testViewPublishedDocument(self):
        # Owner is allowed
        self.login(TEST_USER_NAME)
        self.assertTrue(checkPerm(View, self.doc))
        # Member is allowed
        self.login('member')
        self.assertTrue(checkPerm(View, self.doc))
        # Reviewer is allowed
        self.login('reviewer')
        self.assertTrue(checkPerm(View, self.doc))
        # Anonymous is allowed
        self.logout()
        self.assertTrue(checkPerm(View, self.doc))
        # Editor is allowed
        self.login('editor')
        self.assertTrue(checkPerm(View, self.doc))
        # Reader is allowed
        self.login('reader')
        self.assertTrue(checkPerm(View, self.doc))

    # Check access contents info permission

    def testAccessContentsInformationIsNotAcquiredInPublishedState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(AccessContentsInformation), '')   # not checked

    def testAccessPublishedDocument(self):
        # Owner is allowed
        self.login(TEST_USER_NAME)
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Member is allowed
        self.login('member')
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is allowed
        self.login('reviewer')
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Anonymous is allowed
        self.logout()
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Editor is allowed
        self.login('editor')
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Reader is allowed
        self.login('reader')
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))

    def testModifyPortalContentIsNotAcquiredInPublishedState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(ModifyPortalContent), '')

    def testModifyPublishedDocument(self):
        # Owner is allowed
        self.login(TEST_USER_NAME)
        self.assertTrue(checkPerm(ModifyPortalContent, self.doc))
        # Member is denied
        self.login('member')
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Reviewer is denied
        self.login('reviewer')
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Anonymous is denied
        self.logout()
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))
        # Editor is allowed
        self.login('editor')
        self.assertTrue(checkPerm(ModifyPortalContent, self.doc))
        # Reader is denied
        self.login('reader')
        self.assertFalse(checkPerm(ModifyPortalContent, self.doc))

    # Check change events permission

    def testChangeEventsIsNotAcquiredInPublishedState(self):
        # since r104169 event content doesn't use `ChangeEvents` anymore...
        self.assertEqual(self.ni.acquiredRolesAreUsedBy(ModifyPortalContent), '')

    def testModifyPublishEvent(self):
        # Owner is allowed
        self.assertTrue(checkPerm(ChangeEvents, self.ni))
        # Member is denied
        self.login('member')
        self.assertFalse(checkPerm(ChangeEvents, self.ni))
        # Reviewer is denied
        self.login('reviewer')
        self.assertFalse(checkPerm(ChangeEvents, self.ni))
        # Anonymous is denied
        self.logout()
        self.assertFalse(checkPerm(ChangeEvents, self.ni))
        # Editor is allowed
        self.login('editor')
        self.assertTrue(checkPerm(ChangeEvents, self.ni))
        # Reader is denied
        self.login('reader')
        self.assertFalse(checkPerm(ChangeEvents, self.ni))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOneStateWorkflow))
    return suite
