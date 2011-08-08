from zope.interface import implements
from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from kss.core.interfaces import IKSSView
from plone.app.kss.plonekssview import PloneKSSView as base


class KSSSharingView(base):
    """KSS view for sharing page.
    """
    implements(IKSSView)

    template = ViewPageTemplateFile('sharing.pt')
    macro_wrapper = ViewPageTemplateFile('macro_wrapper.pt')

    def updateSharingInfo(self, search_term=''):
        sharing = getMultiAdapter((self.context, self.request), name="sharing")

        # get the html from a macro
        ksscore = self.getCommandSet('core')

        the_id = 'user-group-sharing'
        macro = self.template.macros[the_id]
        res = self.macro_wrapper(the_macro=macro, instance=self.context, view=sharing)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(the_id), res)
        self.issueAllPortalMessages()
        return self.render()
