from plone.app.workflow import permissions
from plone.app.workflow import PloneMessageFactory as _
from plone.app.workflow.interfaces import ISharingPageRole
from zope.interface import implementer


@implementer(ISharingPageRole)
class ReaderRole:

    title = _("title_can_view", default="Can view")
    required_permission = permissions.DelegateReaderRole
    required_interface = None


@implementer(ISharingPageRole)
class EditorRole:

    title = _("title_can_edit", default="Can edit")
    required_permission = permissions.DelegateEditorRole
    required_interface = None


@implementer(ISharingPageRole)
class ContributorRole:

    title = _("title_can_add", default="Can add")
    required_permission = permissions.DelegateContributorRole
    required_interface = None


@implementer(ISharingPageRole)
class ReviewerRole:

    title = _("title_can_review", default="Can review")
    required_permission = permissions.DelegateReviewerRole
    required_interface = None
