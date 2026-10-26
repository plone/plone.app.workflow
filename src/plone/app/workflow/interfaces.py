from zope import schema
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface.interfaces import IObjectEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class ILocalrolesModifiedEvent(IObjectModifiedEvent):
    """Interface for event which get fired after local roles of an object has
    been changed.
    """


class IPrincipalLocalRolesModifiedEvent(IObjectEvent):
    """The local roles of a user or group on an object have been changed
    through the sharing view, for each user or group whose roles changed.

    Unlike ``ILocalrolesModifiedEvent``, this tells what has changed,
    e.g. for audit logging.
    """

    principal_id = Attribute("Id of the user or group")
    old_roles = Attribute("Sorted tuple of the local roles before the change")
    new_roles = Attribute("Sorted tuple of the local roles after the change")


class ILocalRolesInheritanceModifiedEvent(IObjectEvent):
    """Inheriting local roles from the parent has been switched on or off
    for an object through the sharing view.
    """

    inherit = Attribute("True if the object now inherits local roles")


class ISharingPageRole(Interface):
    """A named utility providing information about roles that are managed
    by the sharing page.

    Utility names should correspond to the role name.

    A user will be able to delegate the given role if a utility can be found
    and the user has the required_permission (or it's None).
    """

    title = schema.TextLine(title="A friendly name for the role")

    required_permission = schema.TextLine(
        title="Permission required to manage this local role", required=False
    )

    required_interface = schema.Object(
        schema=Interface,
        title="Context interface required to display this role",
        required=False,
    )
