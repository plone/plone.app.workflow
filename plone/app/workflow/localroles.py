from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from plone.app.workflow import permissions

from Products.CMFPlone import PloneMessageFactory as _

# These are for everyone

class ReaderRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_can_view", default=u"Can view")
    required_permission = permissions.DelegateReaderRole
    
class EditorRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_can_edit", default=u"Can edit")
    required_permission = permissions.DelegateEditorRole
    
class ContributorRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_can_add", default=u"Can add")
    required_permission = permissions.DelegateContributorRole
    
class ReviewerRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_can_review", default=u"Can review")
    required_permission = permissions.DelegateReviewerRole

# Only managers can manage these

# class ManagerRole(object):
#     implements(ISharingPageRole)
#     
#     title = u"Manage"
#     required_permission = 'Manage portal'
#     
# class OwnerRole(object):
#     implements(ISharingPageRole)
#     
#     title = u"Own"
#     required_permission = 'Manage portal'
#     
# class MemberRole(object):
#     implements(ISharingPageRole)
#     
#     title = u"Member"
#     required_permission = 'Manage portal'
