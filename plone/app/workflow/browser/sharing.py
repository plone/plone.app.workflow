from Products.Five.browser import BrowserView

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName

from plone.memoize.instance import memoize

class SharingView(BrowserView):
    
    # Actions
    
    def update(self, redirect=True):
        """Perform the update and redirect
        """
        
        # This is a bit complex, since the form hides a lot of complexity
        
        # - Read the settings for users. If there is nothing selected for a 
        # user, remove all local roles for that user, else update local roles
        # as per the settings (note, a missing value in the request means)
        # the role should be taken away!
        
        # - Ditto for groups
        
        # - If there was no add or user query, redirect back to the view,
        # else return to @@sharing
        
        if redirect:
            search_term = self.request.get('search_term', None)
            users_to_add = self.request.get('add_users', None)
            groups_to_add = self.request.get('add_groups', None)
        
            if not search_term and not users_to_add and not groups_to_add:
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
        # Can we use Zope 3 role interfaces for this?
        
        return [dict(id='Reader',   title='View'),
                dict(id='Editor',   title='Edit'),
                dict(id='Reviewer', title='Reviewer')]
        
    @memoize
    def role_settings(self):
        """Get current settings for users and groups for which settings have been made.
        
        Returns a list of dicts with keys:
        
         - id
         - title
         - type (one of 'group' or 'user')
         - roles
         
        'roles' is a list of settings, one per role as returned by roles(),
        each containing the values True if the role is explicitly set, False
        if the role is explicitly disabled and None if the role is inherited.
        """
        
        portal_membership = getToolByName(aq_inner(self.context), 'portal_membership')
        portal_groups = getToolByName(aq_inner(self.context), 'portal_groups')
        portal = getToolByName(aq_inner(self.context), 'portal_url').getPortalObject()
        acl_users = getattr(portal, 'acl_users')
        
        info = []
        local_roles = acl_users.getLocalRolesForDisplay(context)
        inherited_roles = self._inherited_roles()
        
        # TODO: Need to convert logic from computeRoleMap.py
        # to here
        
        # Note if a user was selected to be added, must return this with no
        # roles selected
        
        users_to_add = self.request.get('add_users', [])
        for user_id in users_to_add:
            m = portal_membership.getMemberById(user_id)
            info.append(dict(id=m.getId(),
                             title=m.getProperty('fullname', None) or m.getUserName(),
                             roles=[]))
                             
        groups_to_add = self.request.get('add_groups', [])
        for group_id in groups_to_add:
            g = portal_groups.getGroupById(user_id)
            info.append(dict(id=g.getId(),
                             title=g.getGroupTitleOrName(),
                             roles=[]))
                             
        return info
        
    def inherited(self, context=None):
        """Return True if local roles are inherited here.
        """
        if context is None:
            context = aq_inner(self.context)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        acl_users = getattr(portal, 'acl_users')
        return acl_users.isLocalRoleAcquired(aq_inner(self.context))
        
    def user_search_results(self):
        """Return search results for a query to add new users
        
        Returns a list of dicts, with keys:
        
         - id
         - title
         
        """
        search_term = self.request.get('search_term', None)
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
        search_term = self.request.get('search_term', None)
        groups = []
        existing_groups = [g['id'] for g in self.group_settings() if u['type'] == 'group']
        if search_term:
            portal_groups = getToolByName(aq_inner(self.context), 'portal_groups')
            for g in portal_groups.searchForGroups(name=search_term):
                groups.append(dict(id=g.getId(),
                                   title=g.getGroupTitleOrName()))
        return groups
        
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