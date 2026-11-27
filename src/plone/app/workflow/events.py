from plone.app.workflow.interfaces import ILocalRolesInheritanceModifiedEvent
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from plone.app.workflow.interfaces import IPrincipalLocalRolesModifiedEvent
from zope.interface import implementer
from zope.interface.interfaces import ObjectEvent
from zope.lifecycleevent import ObjectModifiedEvent


@implementer(ILocalrolesModifiedEvent)
class LocalrolesModifiedEvent(ObjectModifiedEvent):
    """Gets fired after local roles of an object has been changed."""


@implementer(IPrincipalLocalRolesModifiedEvent)
class PrincipalLocalRolesModifiedEvent(ObjectEvent):
    """Gets fired for each user or group whose local roles on an object
    have been changed through the sharing view.
    """

    def __init__(self, object, principal_id, old_roles, new_roles):
        super().__init__(object)
        self.principal_id = principal_id
        self.old_roles = tuple(sorted(old_roles))
        self.new_roles = tuple(sorted(new_roles))


@implementer(ILocalRolesInheritanceModifiedEvent)
class LocalRolesInheritanceModifiedEvent(ObjectEvent):
    """Gets fired after inheriting local roles has been switched on or off
    for an object through the sharing view.
    """

    def __init__(self, object, inherit):
        super().__init__(object)
        self.inherit = inherit
