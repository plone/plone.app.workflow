from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole

class ReaderRole(object):
    implements(ISharingPageRole)
    
    title = u"View"
    required_roles = ()
    
class EditorRole(object):
    implements(ISharingPageRole)
    
    title = u"Edit"
    required_roles = ()
    
class ReviewerRole(object):
    implements(ISharingPageRole)
    
    title = u"Review"
    required_roles = ()