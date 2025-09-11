from plone.app.testing import applyProfile
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from Products.CMFCore.utils import getToolByName

import doctest


class PloneAppWorkflowLayer(PloneSandboxLayer):
    def setUpZope(self, app, configurationContext):
        import plone.app.workflow

        self.loadZCML(package=plone.app.workflow)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.app.contenttypes:default")

        acl_users = getToolByName(portal, "acl_users")

        acl_users.userFolderAddUser(
            "manager",
            "secret",
            [
                "Manager",
            ],
            [],
        )
        acl_users.userFolderAddUser(
            "member",
            "secret",
            [
                "Member",
            ],
            [],
        )
        acl_users.userFolderAddUser(
            "owner",
            "secret",
            [
                "Owner",
            ],
            [],
        )
        acl_users.userFolderAddUser(
            "reviewer",
            "secret",
            [
                "Reviewer",
            ],
            [],
        )
        acl_users.userFolderAddUser(
            "editor",
            "secret",
            [
                "Editor",
            ],
            [],
        )
        acl_users.userFolderAddUser(
            "reader",
            "secret",
            [
                "Reader",
            ],
            [],
        )

        acl_users.userFolderAddUser(
            "delegate_reader",
            "secret",
            [
                "Member",
            ],
            [],
        )
        acl_users.userFolderAddUser(
            "delegate_editor",
            "secret",
            [
                "Member",
            ],
            [],
        )
        acl_users.userFolderAddUser(
            "delegate_contributor",
            "secret",
            [
                "Member",
            ],
            [],
        )
        acl_users.userFolderAddUser(
            "delegate_reviewer",
            "secret",
            [
                "Member",
            ],
            [],
        )


PLONE_APP_WORKFLOW_FIXTURE = PloneAppWorkflowLayer()

PLONE_APP_WORKFLOW_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_WORKFLOW_FIXTURE,),
    name="PloneAppWorkflowLayer:Integration",
)

PLONE_APP_WORKFLOW_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_WORKFLOW_FIXTURE,),
    name="PloneAppWorkflowLayer:Functional",
)

optionflags = (
    doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
)
