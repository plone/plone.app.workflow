from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole

class ReaderRole(object):
    implements(ISharingPageRole)
    
    title = u"View"
    
class EditorRole(object):
    implements(ISharingPageRole)
    
    title = u"Edit"
    
class ReviewerRole(object):
    implements(ISharingPageRole)
    
    title = u"Review"