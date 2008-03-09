from Products.CMFCore.permissions import setDefaultRoles

DelegateRoles = "Sharing page: Delegate roles"
DelegateReaderRole = "Sharing page: Delegate Reader role"
DelegateEditorRole = "Sharing page: Delegate Editor role"
DelegateContributorRole = "Sharing page: Delegate Contributor role"
DelegateReviewerRole = "Sharing page: Delegate Reviewer role"

# Controls access to the "sharing" page
setDefaultRoles(DelegateRoles, ('Manager', 'Owner', 'Editor', 'Reviewer', ))

# Control the individual roles
setDefaultRoles(DelegateReaderRole, ('Manager', 'Owner', 'Editor', 'Reviewer'))
setDefaultRoles(DelegateEditorRole, ('Manager', 'Owner', 'Editor'))
setDefaultRoles(DelegateContributorRole, ('Manager', 'Owner',))
setDefaultRoles(DelegateReviewerRole, ('Manager', 'Reviewer',))