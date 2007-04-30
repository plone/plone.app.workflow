from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole

from Products.CMFPlone import PloneMessageFactory as _

# These are for everyone

class ReaderRole(object):
    implements(ISharingPageRole)
    
    title = _(u"Can view")
    required_permission = None
    
class EditorRole(object):
    implements(ISharingPageRole)
    
    title = _(u"Can edit")
    required_permission = None
    
class ContributorRole(object):
    implements(ISharingPageRole)
    
    title = _(u"Can add")
    required_permission = None
    
class ReviewerRole(object):
    implements(ISharingPageRole)
    
    title = _(u"Can review")
    required_permission = None
    
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