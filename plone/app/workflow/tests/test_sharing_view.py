from borg.localrole.interfaces import ILocalRoleProvider
from plone.app.testing import login
from plone.app.workflow.events import LocalrolesModifiedEvent
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from plone.app.workflow.testing import PLONE_APP_WORKFLOW_INTEGRATION_TESTING
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import adapter
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.event import notify
from zope.interface import implementer
from zope.interface import Interface

import unittest


class TestSharingView(unittest.TestCase):

    layer = PLONE_APP_WORKFLOW_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.acl_users._doAddUser("testuser", "secret", ["Member"], [])
        self.portal.acl_users._doAddUser("testreviewer", "secret", ["Reviewer"], [])
        self.portal.acl_users._doAddUser("nonasciiuser", "secret", ["Member"], [])
        self.portal.acl_users._doAddGroup(
            "testgroup", [], title="Some meaningful title"
        )
        testuser = self.portal.portal_membership.getMemberById("testuser")
        testuser.setMemberProperties(dict(email="testuser@plone.org"))
        nonasciiuser = self.portal.portal_membership.getMemberById("nonasciiuser")
        nonasciiuser.setMemberProperties(dict(fullname="\xc4\xdc\xdf"))
        login(self.portal, "manager")

    def test_search_by_login_name(self):
        """Make sure we can search by login name on the Sharing tab.

        Prevents regressions of #6853.
        """
        self.request.form["search_term"] = "testuser"
        view = getMultiAdapter((self.portal, self.request), name="sharing")
        results = view.user_search_results()
        self.assertTrue(len(results))
        self.assertEqual(
            results[0].get("id"),
            "testuser",
            msg="Didn't find testuser when I searched by login name.",
        )
        self.assertEqual(
            results[0].get("login"),
            "testuser",
            msg="Didn't display login when I searched by login name.",
        )

    def _search_by_email(self, term):
        self.request.form["search_term"] = term
        view = getMultiAdapter((self.portal, self.request), name="sharing")
        results = view.user_search_results()
        self.assertTrue(len(results))
        self.assertEqual(
            results[0].get("id"),
            "testuser",
            msg="Didn't find testuser when I searched for %s as email." % term,
        )
        self.assertEqual(
            results[0].get("login"),
            "testuser",
            msg="Didn't display login when I searched for %s as email." % term,
        )

    def test_search_by_email(self):
        """Make sure we can search by email on the Sharing tab.

        Prevents regressions of #11631.
        """
        self._search_by_email("testuser@plone.org")
        self._search_by_email("plone.org")
        self._search_by_email("plone")

    def test_search_with_nonascii_users(self):
        """Make sure we can search with users that have non-ascii-chars in their fullname.

        Prevents regressions of #7576.
        """
        self.request.form["search_term"] = "nonasciiuser"
        view = getMultiAdapter((self.portal, self.request), name="sharing")
        results = view.role_settings()
        self.assertTrue(len(results))
        expected = "ÄÜß"
        self.assertEqual(
            results[-1].get("title"),
            expected,
            msg="Umlaute",
        )

    def test_search_for_group_by_id(self):
        """Make sure we can search for groups by id"""
        self.request.form["search_term"] = "testgroup"
        view = getMultiAdapter((self.portal, self.request), name="sharing")
        results = view.group_search_results()
        self.assertTrue(len(results))
        self.assertEqual(
            results[0].get("id"),
            "testgroup",
            msg="Didn't find testgroup when I searched by group id.",
        )
        self.assertIsNone(results[0].get("login"))

    def test_search_for_group_by_title(self):
        """Make sure we can search for groups by title"""
        self.request.form["search_term"] = "meaningful"
        view = getMultiAdapter((self.portal, self.request), name="sharing")
        results = view.group_search_results()
        self.assertTrue(len(results))
        self.assertEqual(
            results[0].get("title"),
            "Some meaningful title",
            msg="Didn't find testuser when I searched by group title.",
        )

    def test_group_name_links_to_prefs_for_admin(self):
        """Make sure that for admins  group name links to group prefs"""
        self.request.form["search_term"] = "testgroup"
        view = getMultiAdapter((self.portal, self.request), name="sharing")
        self.assertIn(
            '<a href="http://nohost/plone/@@usergroup-groupmembership?'
            'groupname=testgroup">',
            view(),
            msg="Group name was not linked to group prefs.",
        )

    def test_group_name_links_not_include_authusers(self):
        """Make sure that for admins  group name links to group prefs"""
        self.request.form["search_term"] = "testgroup"
        view = getMultiAdapter((self.portal, self.request), name="sharing")
        self.assertNotIn(
            '<a href="http://nohost/plone/@@usergroup-groupmembership?'
            'groupname=AuthenticatedUsers">',
            view(),
            msg="AuthenticatedUsers was linked to group prefs.",
        )

    def test_group_name_doesnt_link_to_prefs_for_reviewer(self):
        """Make sure that for admins  group name links to group prefs"""
        login(self.portal, "testreviewer")
        self.request.form["search_term"] = "testgroup"
        view = getMultiAdapter((self.portal, self.request), name="sharing")
        self.assertNotIn(
            '<a href="http://nohost/plone/@@usergroup-groupmembership?'
            'groupname=testgroup">',
            view(),
            msg="Group name link was unexpectedly shown to reviewer.",
        )

    def test_local_manager_removes_inheritance(self):
        """When a user that inherits the right to remove inheritance do it,
        its roles are locally set on content
        to avoid him to loose rights on the content itself
        Refs #11945
        """
        self.portal.acl_users._doAddUser("localmanager", "secret", ["Member"], [])
        folder = self.portal[self.portal.invokeFactory("Folder", "folder")]
        subfolder = folder[folder.invokeFactory("Folder", "subfolder")]
        folder.manage_setLocalRoles("localmanager", ("Manager",))

        login(self.portal, "localmanager")
        sharing = subfolder.restrictedTraverse("@@sharing")
        sharing.update_inherit(status=False, reindex=True)

        user = self.portal.portal_membership.getAuthenticatedMember()
        self.assertIn(
            "Manager",
            user.getRolesInContext(subfolder),
        )

    def test_borg_localroles(self):
        @adapter(ISiteRoot)
        @implementer(ILocalRoleProvider)
        class LocalRoleProvider:
            def __init__(self, context):
                self.context = context

            def getAllRoles(self):
                yield "borguser", ("Contributor",)

            def getRoles(self, user_id):
                if user_id == "borguser":
                    return ("Contributor",)
                return ()

        provideAdapter(LocalRoleProvider)

        self.portal.acl_users._doAddUser("borguser", "secret", ["Member"], [])
        login(self.portal, "manager")
        sharing = self.portal.restrictedTraverse("@@sharing")
        info = sharing.existing_role_settings()
        self.assertEqual(2, len(info))
        self.assertEqual("borguser", info[1]["id"])
        self.assertEqual("acquired", info[1]["roles"]["Contributor"])

        # check borg local roles works with non-heriting roles policy
        sharing = self.portal.restrictedTraverse("@@sharing")
        setattr(sharing.context, "__ac_local_roles_block__", True)
        info = sharing.existing_role_settings()
        self.assertEqual(2, len(info))
        self.assertEqual("borguser", info[1]["id"])
        self.assertEqual("acquired", info[1]["roles"]["Contributor"])

    def test_localroles_modified_event(self):
        # define local roles modified sensitive interface and class
        class ILRMEContext(Interface):
            pass

        @implementer(ILRMEContext)
        class LRMEContext:
            def __init__(self):
                # gets set by handler
                self.context = None
                self.event = None

        # define handler
        def lrme_handler(context, event):
            context.context = context
            context.event = event

        # register handler
        gsm = getGlobalSiteManager()
        gsm.registerHandler(lrme_handler, (ILRMEContext, ILocalrolesModifiedEvent))
        # create object and notify subscriber
        context = LRMEContext()
        event = LocalrolesModifiedEvent(context, self.request)
        notify(event)
        # check subscriber called
        self.assertEqual(context.context, context)
        self.assertEqual(context.event, event)
