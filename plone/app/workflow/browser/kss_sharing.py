from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from kss.core.interfaces import IKSSView
from plone.app.kss.azaxview import AzaxBaseView as base

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer

from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.component import getMultiAdapter

class KssSharingView(base):
    """Kss view for sharing page.
    """
    implements(IKSSView)

    template = ViewPageTemplateFile('sharing.pt')
    macro_wrapper = ViewPageTemplateFile('macro_wrapper.pt')

    
    def updateSharingInfo(self, search_term=''):
    
        # get the table body, let it render again
        # use macro in sharing.pt for that

        sharing = getMultiAdapter((self.context, self.request,), name="sharing")

        # get the html from a macro
        the_id = 'user-group-sharing-settings'
        ksscore = self.getCommandSet('core')
        macro = self.template.macros[the_id]
        res = self.macro_wrapper(the_macro=macro, instance=self.context, view=sharing)
        # self.macroContent does not work, it used restrictedTraverse
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(the_id), res)
        the_id = 'user-group-sharing-head'
        macro = self.template.macros[the_id]
        res = self.macro_wrapper(the_macro=macro, instance=self.context, view=sharing)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(the_id), res)
        return self.render()

