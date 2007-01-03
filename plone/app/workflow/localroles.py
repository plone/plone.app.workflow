from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole

# These are for everyone

class ReaderRole(object):
    implements(ISharingPageRole)
    
    title = u"View"
    required_permission = None
    
class EditorRole(object):
    implements(ISharingPageRole)
    
    title = u"Edit"
    required_permission = None
    
class ReviewerRole(object):
    implements(ISharingPageRole)
    
    title = u"Review"
    required_permission = None
    
# Only managers can manage these
    
class ManagerRole(object):
    implements(ISharingPageRole)
    
    title = u"Manage"
    required_permission = 'Manage portal'
    
class OwnerRole(object):
    implements(ISharingPageRole)
    
    title = u"Own"
    required_permission = 'Manage portal'
    
class MemberRole(object):
    implements(ISharingPageRole)
    
    title = u"Member"
    required_permission = 'Manage portal'