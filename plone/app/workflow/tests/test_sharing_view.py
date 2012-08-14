#
# Test the sharing browser view.
#

from zope.component import getMultiAdapter

from base import WorkflowTestCase


class TestSharingView(WorkflowTestCase):

    def afterSetUp(self):
        self.portal.acl_users._doAddUser('testuser', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('nonasciiuser', 'secret', ['Member'], [])
        self.portal.acl_users._doAddGroup('testgroup', [], title='Some meaningful title')
        testuser = self.portal.portal_membership.getMemberById('testuser')
        testuser.setMemberProperties(dict(email='testuser@plone.org'))
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
        self.failUnless(len(results) and results[0].get('id') == 'testuser',
            msg="Didn't find testuser when I searched by login name.")

    def search_by_email(self, term):
        request = self.app.REQUEST
        request.form['search_term'] = term
        view = getMultiAdapter((self.portal, request), name='sharing')
        results = view.user_search_results()
        self.failUnless(len(results) and results[0].get('id') == 'testuser',
            msg="Didn't find testuser when I searched for %s as email." % term)

    def test_search_by_email(self):
        """Make sure we can search by email on the Sharing tab.

        Prevents regressions of #11631.
        """
        self.search_by_email('testuser@plone.org')
        self.search_by_email('plone.org')
        self.search_by_email('plone')

    def test_search_with_nonascii_users(self):
        """Make sure we can search with users that have non-ascii-chars in their fullname.

        Prevents regressions of #7576.
        """
        request = self.app.REQUEST
        request.form['search_term'] = 'nonasciiuser'
        view = getMultiAdapter((self.portal, request), name='sharing')
        results = view.role_settings()
        self.failUnless(len(results) and results[1].get('title') == '\xc3\x84\xc3\x9c\xc3\x9f', msg="Umlaute")

    def test_search_for_group_by_id(self):
        """ Make sure we can search for groups by id """
        request = self.app.REQUEST
        request.form['search_term'] = 'testgroup'
        view = getMultiAdapter((self.portal, request), name='sharing')
        results = view.group_search_results()
        self.failUnless(len(results) and results[0].get('id') == 'testgroup',
            msg="Didn't find testgroup when I searched by group id.")

    def test_search_for_group_by_title(self):
        """ Make sure we can search for groups by title """
        request = self.app.REQUEST
        request.form['search_term'] = 'meaningful'
        view = getMultiAdapter((self.portal, request), name='sharing')
        results = view.group_search_results()
        self.failUnless(len(results) and results[0].get('title') == 'Some meaningful title',
            msg="Didn't find testuser when I searched by group title.")

    def test_local_manager_removes_inheritance(self):
        """When a user that inherits the right to remove inheritance do it,
        its roles are locally set on content
        to avoid him to loose rights on the content itself
        Refs #11945
        """
        self.portal.acl_users._doAddUser('localmanager', 'secret', ['Member'], [])
        folder = self.portal[self.portal.invokeFactory('Folder', 'folder')]
        subfolder = folder[folder.invokeFactory('Folder', 'subfolder')]
        folder.manage_setLocalRoles('localmanager', ('Manager',))

        self.login('localmanager')
        sharing = subfolder.restrictedTraverse('@@sharing')
        sharing.update_inherit(status=False, reindex=True)

        user = self.portal.portal_membership.getAuthenticatedMember()
        self.failUnless('Manager' in user.getRolesInContext(subfolder),)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSharingView))
    return suite
