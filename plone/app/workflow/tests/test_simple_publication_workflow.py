from base import WorkflowTestCase
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
ChangeEvents = 'Change portal events'


class TestSimplePublicationWorkflow(WorkflowTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.workflow.setChainForPortalTypes(['Document', 'News Item'], 'simple_publication_workflow')

        self.portal.acl_users._doAddUser('member', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('reviewer', 'secret', ['Reviewer'], [])
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.portal.acl_users._doAddUser('editor', ' secret', ['Editor'], [])
        self.portal.acl_users._doAddUser('reader', 'secret', ['Reader'], [])

        self.folder.invokeFactory('Document', id='doc')
        self.doc = self.folder.doc
        self.folder.invokeFactory('News Item', id='ni')
        self.ni = self.folder.ni

    # Check allowed transitions: two for simple publication workflow

    def testOwnerSubmitAPrivateDocumentAndRetract(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'pending')
        self.workflow.doActionFor(self.doc, 'retract')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')

    # Check some forbidden transitions

    def testOwnerCannotPublishDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')
        self.assertRaises(WorkflowException, self.workflow.doActionFor, self.doc, 'publish')

    # Check view permission

    def testViewIsNotAcquiredInPrivateState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), '')     # not checked

    def testViewPrivateDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')
        # Owner is allowed
        self.login(TEST_USER_NAME)
        self.assertTrue(checkPerm(View, self.doc))
        # Member is denied
        self.login('member')
        self.assertFalse(checkPerm(View, self.doc))
        # Reviewer is denied
        self.login('reviewer')
        self.assertFalse(checkPerm(View, self.doc))
        # Anonymous is denied
        self.logout()
        self.assertFalse(checkPerm(View, self.doc))
        # Editor is allowed
        self.login('editor')
        self.assertTrue(checkPerm(View, self.doc))
        # Reader is allowed
        self.login('reader')
        self.assertTrue(checkPerm(View, self.doc))

    def testViewIsNotAcquiredInPublishedState(self):
        # transition requires Review portal content
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), '')   # not checked

    def testViewPublishedDocument(self):
        # transition requires Review portal content
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'publish')
        # Owner is allowed
        self.login(TEST_USER_NAME)
        self.assertTrue(checkPerm(View, self.doc))
        # Member is allowed
        self.login('member')
        self.assertTrue(checkPerm(View, self.doc))
        # Reviewer is denied  but he acquires through Anonymous Role
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

    def testAccessContentsInformationIsNotAcquiredInPrivateState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(AccessContentsInformation), '')     # not checked

    def testAccessContentsInformationPrivateDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')
        # Owner is allowed
        self.login(TEST_USER_NAME)
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Member is denied
        self.login('member')
        self.assertFalse(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is denied
        self.login('reviewer')
        self.assertFalse(checkPerm(AccessContentsInformation, self.doc))
        # Anonymous is denied
        self.logout()
        self.assertFalse(checkPerm(AccessContentsInformation, self.doc))
        # Editor is allowed
        self.login('editor')
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Reader is allowed
        self.login('reader')
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))

    def testAccessContentsInformationIsNotAcquiredInPublishedState(self):
        # transition requires Review portal content
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(AccessContentsInformation), '') # not checked

    def testAccessContentsInformationPublishedDocument(self):
        # transition requires Review portal content
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'publish')
        # Owner is allowed
        self.login(TEST_USER_NAME)
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Member is allowed
        self.login('member')
        self.assertTrue(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is denied but he acquires through Anonymous Role
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

    # Check modify content permissions

    def testModifyPrivateDocumentIsNotAcquiredInPrivateState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(ModifyPortalContent), '') # not checked

    def testModifyPrivateDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')
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

    def testModifyPortalContentIsNotAcquiredInPublishedState(self):
        # transition requires Review portal content
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(ModifyPortalContent), '')

    def testModifyPublishedDocument(self):
        # transition requires Review portal content
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'publish')
        # Manager is allowed
        self.assertTrue(checkPerm(ModifyPortalContent, self.doc))
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

    def testModifyPrivateEvent(self):
        self.assertEqual(self.workflow.getInfoFor(self.ni, 'review_state'), 'private')
        # Owner is allowed
        self.login(TEST_USER_NAME)
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

    def testModifyPublishEvent(self):
        # transition requires Review portal content
        self.login('manager')
        self.workflow.doActionFor(self.ni, 'publish')
        self.assertTrue(checkPerm(ChangeEvents, self.ni))
        # Owner is allowed
        self.login(TEST_USER_NAME)
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
    suite.addTest(makeSuite(TestSimplePublicationWorkflow))
    return suite
