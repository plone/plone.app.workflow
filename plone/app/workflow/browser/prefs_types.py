from zope.component import getUtilitiesFor, queryUtility

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

from plone.memoize.instance import memoize, clearafter

from plone.app.workflow.interfaces import ISharingPageRole

class PrefsTypesView(BrowserView):
    
    # Actions
    
    template = ViewPageTemplateFile('prefs_types.pt')
    
    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        
        postback = True
        
        form = self.request.form
        submitted = form.get('form.submitted', False)
    
        save_button = form.get('form.button.Save', None) is not None
        cancel_button = form.get('form.button.Cancel', None) is not None
    
        if submitted and not cancel_button:
            
            # Update the acquire-roles setting
            inherit = bool(form.get('inherit', False))
            self.update_inherit(inherit)

            # Update settings for users and groups
            entries = form.get('entries', [])
            roles = [r['id'] for r in self.roles()]
            settings = []
            for entry in entries:
                settings.append(
                    dict(id = entry['id'],
                         type = entry['type'],
                         roles = [r for r in roles if entry.get('role_%s' % r, False)]))
            if settings:
                self.update_role_settings(settings)
            
        # Other buttons return to the sharing page
        if save_button or cancel_button:
            postback = False
        
        if postback:
            return self.template()
        else:
            self.request.response.redirect(self.context.absolute_url())
            
    # View

    @memoize
    def current_workflow(self, type_id):
        """Given the portal type return the current workflow
        """
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        try: 
            return portal_workflow.getChainForPortalType(type_id)[0]
        except IndexError:
            return ''

    @memoize
    def is_type_selected(self, type, type_id):
        """Has this type been selected in the drop down menu?
        """
        context = aq_inner(self.context)
        portal_types = getToolByName(self, 'portal_types')
        if (type.Title() == portal_types[type_id].Title()):
            return ('selected')

    @memoize
    def states_for_new_workflow(self, wf_id):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        if wf_id == 'No change':
            return None
        else:
            return (portal_workflow[wf_id].states.keys())

    @memoize
    def states_for_current_workflow(self, type_id):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')

        try: 
            return (portal_workflow[portal_workflow.getChainForPortalType(type_id)[0]].states.keys())
        except:
            return ''

    @memoize
    def is_wf_selected(self, wf, wf_id):
        """Has this workflow been selected in the drop down menu?
        """
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')

        if wf_id == 'No change':
            return None
        elif (wf.id == portal_workflow[wf_id].id):
            return ('selected')
    
    @memoize
    def re_map_states(self):

        """Based on manage_catalogRebuild and clearFindAndRebuild from
            CatalogTool    
        """

        elapse = time.time()
        c_elapse = time.clock()
        self.clearFindAndRebuild()
        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse
        if RESPONSE is not None:
            RESPONSE.redirect(
              URL1 + '/manage_catalogAdvanced?manage_tabs_message=' +
              urllib.quote('Catalog Rebuilt\n'
                           'Total time: %s\n'
                           'Total CPU time: %s' % (`elapse`, `c_elapse`)))
        def indexObject(obj, path):
            if (base_hasattr(obj, 'indexObject') and
                safe_callable(obj.indexObject)):
                try:
                    obj.indexObject()
                except TypeError:
                    # Catalogs have 'indexObject' as well, but they
                    # take different args, and will fail
                    pass
        self.manage_catalogClear()
        portal = aq_parent(aq_inner(self))
        portal.ZopeFindAndApply(portal, search_sub=True, apply_func=indexObject)
