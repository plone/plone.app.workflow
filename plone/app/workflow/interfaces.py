from zope.interface import Interface
from zope import schema

class ISharingPageRole(Interface):
    """A named utility providing information about roles that are managed
    by the sharing page.
    
    Utility names should correspond to the role name.
    """
    
    title = schema.TextLine(title=u"A friendly name for the role")
    
    required_permission = schema.TextLine(title=u"Permission required to manag this local role",
                                          required=False)
