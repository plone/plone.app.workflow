from zope.interface import Interface
from zope import schema

class ISharingPageRole(Interface):
    """A named utility providing information about roles that are managed
    by the sharing page.
    
    Utility names should correspond to the role name.
    """
    
    title = schema.TextLine(title=u"A friendly name for the role")
    
    required_roles = schema.Tuple(title=u"List of roles acceptable in managing this local role",
                                  description=u"An empty list means any role can manage this local role",
                                  required=False,
                                  value_type=schema.TextLine(title=u""))
    