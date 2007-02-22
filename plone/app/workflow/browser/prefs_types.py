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
            CatalogTool and/or code from Tesdal (non working atm)
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

        wf_mapping = { ( 'plone_workflow', 'abm_workflow') :
                         { 'private'   : 'draft'
                         , 'visible'   : 'draft'
                         , 'pending'   : 'pending'
                         , 'published' : 'published'
                         }
                     , ( 'folder_workflow', 'abm_workflow') :
                         { 'private'   : 'draft'
                         , 'visible'   : 'draft'
                         , 'published' : 'published'
                         }
                     }
         
        def change_workflow(self):
            """ Changes the workflow on all objects recursively from self """
            # XXX DOES THIS WORK WITH PLACEFUL WORKFLOW?
         
            # Set up variables
            portal = self.portal_url.getPortalObject()
            typestool = getToolByName(self, 'portal_types')
            wftool = getToolByName(self, 'portal_workflow')
            cbt = wftool._chains_by_type
         
            def walk(obj):
                num = 0
                portal_type = getattr(aq_base(obj), 'portal_type', None)
                if portal_type is not None:
                    chain = cbt.get(portal_type, None)
                    if chain is None or chain:
                        if chain is None:
                            chain = wftool._default_chain
                        if hasattr(obj, 'workflow_history'):
                            wf_hist = getattr(obj, 'workflow_history', {})
                            for key in wf_hist.keys():
                                for to_wf in chain:
                                    mapping = wf_mapping.get((key,to_wf), {})
                                    if mapping:
                                        wf_entries = wf_hist[key]
                                        last_entry = wf_entries[-1]
                                        if not mapping[last_entry['review_state']] == last_entry['review_state']:
                                            # We need to insert a transition
                                            transition = { 'action'       : 'script_migrate'
                                                         , 'review_state' : mapping[last_entry['review_state']]
                                                         , 'actor'        : last_entry['actor']
                                                         , 'comments'     : last_entry['comments']
                                                         , 'time'         : last_entry['time']
                                                         }
                                            wf_entries = wf_entries + (transition,)
         
                                        # After massaging and changing, we're ready to reassign
                                        del wf_hist[key]
                                        wf_hist[to_wf] = wf_entries
         
                            obj.workflow_history = wf_hist
                            obj.reindexObject(idxs=['allowedRolesAndUsers','review_state'])
                            num = 1
         
                objlist = []
                if hasattr(aq_base(obj), 'objectValues') and \
                   not getattr(aq_base(obj), 'isLayerLanguage', 0):
                    objlist = list(aq_base(obj).objectValues())
                if hasattr(aq_base(obj), 'opaqueValues'):
                    objlist += list(obj.opaqueValues())
                for o in objlist:
                    num += walk(o)
                return num
         
            num = 0
            # Iterate over objects, changing the workflow id in the workflow_history
            objlist = list(self.objectValues())
            if hasattr(self, 'opaqueValues'):
                objlist += list(self.opaqueValues())
            for o in objlist:
                num += walk(o)
           
            # Return the number of objects for which we changed workflow
            return num 
