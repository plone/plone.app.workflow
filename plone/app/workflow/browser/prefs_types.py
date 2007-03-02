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

            # Update content type title
            plone_tool = getToolByName(self, 'plone_utils')
            types_tool = getToolByName(self, 'portal_types')
            type_id = form['type_id']
            title = form['title']
            #types_list = plone_tool.getUserFriendlyTypes()
            types_dict = types_tool.listTypeTitles()
            if type_id in types_dict:
                if types_dict[type_id] != title:
                    #print ("setting title for ", title)
                    ti = types_tool.getTypeInfo(type_id)
                    ti.title = title

            # Update workflow 
            #portal_workflow = getToolByName(self, 'portal_workflow')
            #portal_workflow.setChainForPortalTypes((form['type_id'],), (form['wf_id'],))

            # Update workflow state mappings
            #self.change_workflow()
            #self.request.response.redirect(self.context.absolute_url())
            return self.template()

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
            return ((portal_workflow[portal_workflow.getChainForPortalType(type_id)[0]]).title)
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
    def is_type_globally_allowed(self, type):
        """Is this type globally allowed? 
        """
        return ''

    @memoize
    def is_type_discussion_allowed(self, type):
        """Is this type configured to allow discussion?
        """
        return ''

    @memoize
    def is_type_versionable(self, type_id):
        """Is this type versionable?
        """
        context = aq_inner(self.context)
        portal_repository = getToolByName(context, 'portal_repository')
        return (type_id in portal_repository.getVersionableContentTypes())

    @memoize
    def is_type_searchable(self, type_id):
        """Is this type searchable?
        """
        context = aq_inner(self.context)
        portal_properties = getToolByName(context, 'portal_properties')
        blacklisted = portal_properties.site_properties.types_not_searched
        return (type_id not in blacklisted)

    @memoize
    def wf_title_for_id(self, wf_id):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        try:
            return (portal_workflow[wf_id].title)
        except IndexError:
            return ''
 
    @memoize
    def states_for_new_workflow(self, wf_id):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        if wf_id == 'No Change':
            return None
        else:
            if wf_id == 'No Workflow':
                return ''
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
        if wf_id == 'No Change':
            return ''
        else:
            if (wf_id != 'No Workflow'):
                if (wf.id == portal_workflow[wf_id].id):
                    return 'selected'
    @memoize
    def user_friendly_types(self):
        plone_tool = getToolByName(self, 'plone_utils')
        portal_types = plone_tool.getUserFriendlyTypes()
        return portal_types

    @memoize
    def change_workflow(self):
        """ Changes the workflow on all objects recursively from self """
        # XXX DOES THIS WORK WITH PLACEFUL WORKFLOW?
     
        # Set up variables
        portal = getToolByName(aq_inner(self.context), 'portal_url').getPortalObject()
        typestool = getToolByName(self, 'portal_types')
        wftool = getToolByName(self, 'portal_workflow')

        cbt = wftool._chains_by_type

        wf_mapping = { ( 'plone_workflow', 'community_workflow') :
                     { 'private'   : 'private'
                     , 'visible'   : 'public_draft'
                     , 'pending'   : 'pending'
                     , 'published' : 'published'
                     }
                 }
     
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
                                mapping = wf_mapping.get((key,'community_workflow'), {})
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
        objlist = list(portal.objectValues())
        if hasattr(self, 'opaqueValues'):
            objlist += list(self.opaqueValues())
        for o in objlist:
            if o.id == 'front-page': 
                num += walk(o)
       
        # Return the number of objects for which we changed workflow
        return num 
