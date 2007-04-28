from zope.interface import implements
from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from kss.core.interfaces import IKSSView
from plone.app.kss.azaxview import AzaxBaseView as base


class KssSharingView(base):
    """Kss view for sharing page.
    """
    implements(IKSSView)

    template = ViewPageTemplateFile('sharing.pt')
    macro_wrapper = ViewPageTemplateFile('macro_wrapper.pt')
    
    def updateSharingInfo(self, search_term='', form_vars={}):
    
        sharing = getMultiAdapter((self.context, self.request,), name="sharing")
    
        inherit = bool(form_vars.get('inherit', False))
        sharing.update_inherit(inherit)
        
        # XXX: This doesn't work because the request marshalling appears to
        # be wrong, especially when there are multiple rows with things 
        # selected.
        entries = form_vars.get('entries', [])
        
        roles = [r['id'] for r in sharing.roles()]
        settings = []
        for entry in entries:
            settings.append(
                dict(id = entry['id'],
                     type = entry['type'],
                     roles = [r for r in roles if entry.get('role_%s' % r, False)]))
        if settings:
            sharing.update_role_settings(settings)

        # get the table body, let it render again
        # use macro in sharing.pt for that

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

