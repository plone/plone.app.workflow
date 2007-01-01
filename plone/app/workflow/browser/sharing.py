from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Acquisition import aq_inner, aq_parent
from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

from plone.memoize.instance import memoize, clearafter

class SharingView(BrowserView):
    
    # Actions
    
    template = ViewPageTemplateFile('sharing.pt')
    
    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        
        postback = True
        
        form = self.request.form
        submitted = form.get('form.submitted', False)
    
        submit_button = form.get('form.button.Submit', None) is not None
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
    def roles(self):
        """Get a list of roles that can be managed.
        
        Returns a list of dics with keys:
        
            - id
            - title
        """
        
        # TODO: Should not hardcode this!
        # Should be possible to whitelist portal roles and provide titles
        
        return [dict(id='Reader',   title='View'),
                dict(id='Editor',   title='Edit'),
                dict(id='Reviewer', title='Review')]
        
    @memoize
    def role_settings(self):
        """Get current settings for users and groups for which settings have been made.
        
        Returns a list of dicts with keys:
        
         - id
         - title
         - type (one of 'group' or 'user')
         - roles
         
        'roles' is a dict of settings, with keys of role ids as returned by 
        roles(), and values True if the role is explicitly set, False
        if the role is explicitly disabled and None if the role is inherited.
        """
        
        context = aq_inner(self.context)
        
        portal_membership = getToolByName(aq_inner(self.context), 'portal_membership')
        portal_groups = getToolByName(aq_inner(self.context), 'portal_groups')
        portal = getToolByName(aq_inner(self.context), 'portal_url').getPortalObject()
        acl_users = getattr(portal, 'acl_users')
        
        info = []
        
        # This logic is adapted from computeRoleMap.py
        
        local_roles = acl_users.getLocalRolesForDisplay(context)
        acquired_roles = self._inherited_roles()
        available_roles = [r['id'] for r in self.roles()]

        # first process acquired roles
        items = {}
        for name, roles, rtype, rid in acquired_roles:
            items[rid] = dict(id       = rid,
                              name     = name,
                              type     = rtype,
                              acquired = roles,
                              local    = [],)
                                
        # second process local roles
        for name, roles, rtype, rid in local_roles:
            if items.has_key(rid):
                items[rid]['local'] = roles
            else:
                items[rid] = dict(id       = rid,
                                  name     = name,
                                  type     = rtype,
                                  acquired = [],
                                  local    = roles,)

        # Sort the list: first Owner role, then groups, then users, and then alphabetically

        dec_users = [('Owner' not in a['local'], a['type'], a['name'], a) for a in items.values()]
        dec_users.sort()
        
        # Add the items to the info dict, assigning full name if possible.
        # Also, recut roles in the format specified in the docstring
        
        for d in dec_users:
            item = d[-1]
            info_item = dict(id    = item['id'],
                             type  = item['type'],
                             title = item['name'],
                             roles = {})
                             
            # Record role settings
            have_roles = False
            for r in available_roles:
                if r in item['acquired']:
                    info_item['roles'][r] = None
                    have_roles = True # we want to show acquired roles
                elif r in item['local']:
                    info_item['roles'][r] = True
                    have_roles = True # at least one role is set
                else:
                    info_item['roles'][r] = False
                    
            # Abort if we have no useful roles to manage
            if not have_roles:
                continue
                             
            # Use full name if possible
            if not item['type'] == 'group':
                member = portal_membership.getMemberInfo(name)
                if member is not None and member['fullname']:
                    info_item['name'] = member['fullname']
                    
            info.append(info_item)

        # Note if a user was selected to be added, must return this with no
        # roles selected
        
        empty_roles = dict([(r, False) for r in available_roles])
        
        users_to_add = self.request.form.get('add_users', [])
        for user_id in users_to_add:
            member = portal_membership.getMemberInfo(user_id)
            if member is not None:
                info.append(dict(id    = user_id,
                                 title = member['fullname'] or member['username'] or user_id,
                                 type  = 'user',
                                 roles = empty_roles.copy()))
                             
        groups_to_add = self.request.form.get('add_groups', [])
        for group_id in groups_to_add:
            g = portal_groups.getGroupById(group_id)
            if g is not None:
                info.append(dict(id    = group_id,
                                 title = g.getGroupTitleOrName(),
                                 type  = 'group',
                                 roles = empty_roles.copy()))
                             
        return info
        
    def inherited(self, context=None):
        """Return True if local roles are inherited here.
        """
        if context is None:
            context = self.context
        if getattr(aq_inner(context), '__ac_local_roles_block__', None):
            return False
        return True
        
    def user_search_results(self):
        """Return search results for a query to add new users
        
        Returns a list of dicts, with keys:
        
         - id
         - title
         
        """
        search_term = self.request.form.get('search_term', None)
        users = []
        existing_users = [u['id'] for u in self.role_settings() if u['type'] == 'user']
        if search_term:
            portal_membership = getToolByName(aq_inner(self.context), 'portal_membership')
            for m in portal_membership.searchForMembers(name=search_term):
                if m.getId() not in existing_users:
                    users.append(dict(id=m.getId(),
                                      title=m.getProperty('fullname', None) or m.getUserName()))
        return users
        
    
    def group_search_results(self):
        """Return search results for a query to add new groups
        
        Returns the same values (and uses the same query parameter) as
        user_search_results().
        """
        search_term = self.request.form.get('search_term', None)
        groups = []
        existing_groups = [g['id'] for g in self.role_settings() if g['type'] == 'group']
        if search_term:
            portal_groups = getToolByName(aq_inner(self.context), 'portal_groups')
            for g in portal_groups.searchForGroups(name=search_term):
                groups.append(dict(id=g.getId(),
                                   title=g.getGroupTitleOrName()))
        return groups
        
    # helper functions
        
    def _inherited_roles(self):
        """Returns a tuple with the acquired local roles."""
        context = aq_inner(self.context)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        result = []
        cont = True
        if portal != context:
            parent = aq_parent(context)
            while cont:
                if not getattr(parent, 'acl_users', False):
                    break
                userroles = parent.acl_users.getLocalRolesForDisplay(parent)
                for user, roles, role_type, name in userroles:
                    # Find user in result
                    found = 0
                    for user2, roles2, type2, name2 in result:
                        if user2 == user:
                            # Check which roles must be added to roles2
                            for role in roles:
                                if not role in roles2:
                                    roles2.append(role)
                            found = 1
                            break
                    if found == 0:
                        # Add it to result and make sure roles is a list so
                        # we may append and not overwrite the loop variable
                        result.append([user, list(roles), role_type, name])
                if parent == portal:
                    cont = False
                elif not self.inherited(parent):
                    # Role acquired check here
                    cont = False
                else:
                    parent = aq_parent(parent)

        # Tuplize all inner roles
        for pos in range(len(result)-1,-1,-1):
            result[pos][1] = tuple(result[pos][1])
            result[pos] = tuple(result[pos])

        return tuple(result)
        
    def update_inherit(self, status=True):
        """Enable or disable local role acquisition on the context.
        """
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')
        
        if not portal_membership.checkPermission(permissions.ModifyPortalContent, context):
            raise Unauthorized

        if not status:
            context.__ac_local_roles_block__ = True
        else:
            if getattr(context, '__ac_local_roles_block__', None):
                context.__ac_local_roles_block__ = None

        context.reindexObjectSecurity()
        
    @clearafter
    def update_role_settings(self, new_settings):
        """Update local role settings and reindex object security if necessary.
        
        new_settings is a list of dicts with keys id, for the user/group id;
        type, being either 'user' or 'group'; and roles, containing the list
        of role ids that are set.
        """
        
        reindex = False
        context = aq_inner(self.context)
        
        current_settings = {}
        for s in self.role_settings():
            current_settings[s['id']] = s
            
        managed_roles = frozenset([r['id'] for r in self.roles()])
        member_ids_to_clear = []
            
        for s in new_settings:
            user_id = s['id']
            new_user = not current_settings.has_key(user_id)
            
            existing_roles = frozenset(context.get_local_roles_for_userid(userid=user_id))
            if new_user:
                acquired_roles = frozenset()
            else:
                acquired_roles = frozenset([r['id'] for r in managed_roles 
                                            if current_settings[user_id]['roles'][r] is None])
            selected_roles = frozenset(s['roles'])
            
            # We will remove those roles that we are managing and which set
            # on the context, but which were not selected
            to_remove = managed_roles & existing_roles - selected_roles
            
            # Leaving us with the roles that we 
            new_roles = selected_roles | existing_roles - acquired_roles - to_remove
            
            # take away roles that we are managing, that were not selected 
            # and which were part of the existing roles
            
            
            if new_roles:
                context.manage_setLocalRoles(user_id, list(new_roles))
                reindex = True
            elif not new_user:
                member_ids_to_clear.append(user_id)
                
        if member_ids_to_clear:
            context.manage_delLocalRoles(userids=member_ids_to_clear)
            reindex = True
        
        if reindex:
            self.context.reindexObjectSecurity()