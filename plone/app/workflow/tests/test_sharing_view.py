#
# Test the sharing browser view.
#

from zope.component import getMultiAdapter

from base import WorkflowTestCase


class TestSharingView(WorkflowTestCase):

    def afterSetUp(self):
        self.portal.acl_users._doAddUser('testuser', 'secret', ['Member'], [])
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


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSharingView))
    return suite