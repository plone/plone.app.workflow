from AccessControl import ModuleSecurityInfo
from AccessControl.Permission import addPermission


security = ModuleSecurityInfo("plone.app.workflow.permissions")

# Controls access to the "sharing" page
security.declarePublic("DelegateRoles")
DelegateRoles = "Sharing page: Delegate roles"
addPermission(
    DelegateRoles,
    (
        "Manager",
        "Site Administrator",
        "Owner",
        "Editor",
        "Reviewer",
    ),
)

# Control the individual roles
security.declarePublic("DelegateReaderRole")
DelegateReaderRole = "Sharing page: Delegate Reader role"
addPermission(
    DelegateReaderRole,
    ("Manager", "Site Administrator", "Owner", "Editor", "Reviewer"),
)

security.declarePublic("DelegateEditorRole")
DelegateEditorRole = "Sharing page: Delegate Editor role"
addPermission(
    DelegateEditorRole,
    ("Manager", "Site Administrator", "Owner", "Editor"),
)

security.declarePublic("DelegateContributorRole")
DelegateContributorRole = "Sharing page: Delegate Contributor role"
addPermission(
    DelegateContributorRole,
    (
        "Manager",
        "Site Administrator",
        "Owner",
    ),
)

security.declarePublic("DelegateReviewerRole")
DelegateReviewerRole = "Sharing page: Delegate Reviewer role"
addPermission(
    DelegateReviewerRole,
    (
        "Manager",
        "Site Administrator",
        "Reviewer",
    ),
)
