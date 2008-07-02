from Acquisition import aq_inner
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

        sharing = getMultiAdapter((self.context, self.request,), name="sharing")
    
        inherit = bool(self.request.form.get('inherit', False))
        reindex = sharing.update_inherit(inherit, reindex=False)
        
        # Extract currently selected setting from the form
        # to take these into account (also on re-submit of the form).
        entries = self.request.form.get('entries', [])
        
        roles = [r['id'] for r in sharing.roles()]
        settings = []
        for entry in entries:
            settings.append(
                dict(id = entry['id'],
                     type = entry['type'],
                     roles = [r for r in roles if entry.get('role_%s' % r, False)]))
        if settings:
            reindex = sharing.update_role_settings(settings) or reindex

        if reindex:
            aq_inner(self.context).reindexObjectSecurity()

        # get the table body, let it render again
        # use macro in sharing.pt for that

        # get the html from a macro
        ksscore = self.getCommandSet('core')

        the_id = 'user-group-sharing'
        macro = self.template.macros[the_id]
        res = self.macro_wrapper(the_macro=macro, instance=self.context, view=sharing)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(the_id), res)

        return self.render()

