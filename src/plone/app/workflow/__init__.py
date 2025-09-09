# Register the permissions with Zope
from zope.i18nmessageid import MessageFactory

import plone.app.workflow.permissions  # noqa: F401


PloneMessageFactory = MessageFactory("plone")
