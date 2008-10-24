#
# Test the sharing browser view.
#

from zope.component import getMultiAdapter

from base import WorkflowTestCase


class TestSharingView(WorkflowTestCase):

    def afterSetUp(self):
        self.portal.acl_users._doAddUser('testuser', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('nonasciiuser', 'secret', ['Member'], [])
        nonasciiuser = self.portal.portal_membership.getMemberById('nonasciiuser')
        nonasciiuser.setMemberProperties(dict(fullname=u'\xc4\xdc\xdf'.encode('utf-8')))
        self.loginAsPortalOwner()

    def test_search_by_login_name(self):
        """Make sure we can search by login name on the Sharing tab.
        
        Prevents regressions of #6853.
        """
        request = self.app.REQUEST
        request.form['search_term'] = 'testuser'
        view = getMultiAdapter((self.portal, request), name='sharing')
        results = view.user_search_results()
        self.failUnless(len(results) and results[0].get('id') == 'testuser', msg="Didn't find testuser when I searched by login name.")

    def test_search_with_nonascii_users(self):
        """Make sure we can search with users that have non-ascii-chars in their fullname.
        
        Prevents regressions of #7576.
        """
        request = self.app.REQUEST
        request.form['search_term'] = 'nonasciiuser'
        view = getMultiAdapter((self.portal, request), name='sharing')
        results = view.role_settings()
        self.failUnless(len(results) and results[1].get('title') == '\xc3\x84\xc3\x9c\xc3\x9f', msg="Umlaute")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSharingView))
    return suite
