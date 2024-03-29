from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_parent
from itertools import chain
from plone.app.workflow import PloneMessageFactory as _
from plone.app.workflow.events import LocalrolesModifiedEvent
from plone.app.workflow.interfaces import ISharingPageRole
from plone.base.utils import safe_text
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import clearafter
from plone.memoize.instance import memoize
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import Forbidden
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate

import json


AUTH_GROUP = "AuthenticatedUsers"
STICKY = (AUTH_GROUP,)


def merge_search_results(results, key):
    """Merge member search results.

    Based on PlonePAS.browser.search.PASSearchView.merge.
    """
    output = {}
    for entry in results:
        id = entry[key]
        if id not in output:
            output[id] = entry.copy()
        else:
            buf = entry.copy()
            buf.update(output[id])
            output[id] = buf

    return output.values()


class SharingView(BrowserView):
    # Actions

    template = ViewPageTemplateFile("sharing.pt")
    macro_wrapper = ViewPageTemplateFile("macro_wrapper.pt")

    STICKY = STICKY

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page"""
        postback = self.handle_form()
        if postback:
            return self.template()
        else:
            context_state = self.context.restrictedTraverse("@@plone_context_state")
            url = context_state.view_url()
            self.request.response.redirect(url)

    def handle_form(self):
        """
        We split this out so we can reuse this for ajax.
        Will return a boolean if it was a post or not
        """
        postback = True

        form = self.request.form
        submitted = form.get("form.submitted", False)
        save_button = form.get("form.button.Save", None) is not None
        cancel_button = form.get("form.button.Cancel", None) is not None
        if submitted and save_button and not cancel_button:
            if not self.request.get("REQUEST_METHOD", "GET") == "POST":
                raise Forbidden

            authenticator = self.context.restrictedTraverse("@@authenticator", None)
            if not authenticator.verify():
                raise Forbidden

            # Update the acquire-roles setting
            if self.can_edit_inherit():
                inherit = bool(form.get("inherit", False))
                reindex = self.update_inherit(inherit, reindex=False)
            else:
                reindex = False

            # Update settings for users and groups
            entries = form.get("entries", [])
            roles = [r["id"] for r in self.roles()]
            settings = []
            for entry in entries:
                settings.append(
                    dict(
                        id=entry["id"],
                        type=entry["type"],
                        roles=[r for r in roles if entry.get("role_%s" % r, False)],
                    )
                )
            if settings:
                reindex = self.update_role_settings(settings, reindex=False) or reindex
            if reindex:
                self.context.reindexObjectSecurity()
                notify(LocalrolesModifiedEvent(self.context, self.request))
            IStatusMessage(self.request).addStatusMessage(
                _("Changes saved."), type="info"
            )

        # Other buttons return to the sharing page
        if cancel_button:
            postback = False

        return postback

    # View

    @memoize
    def roles(self):
        """Get a list of roles that can be managed.

        Returns a list of dicts with keys:

            - id
            - title
        """
        context = self.context
        portal_membership = getToolByName(context, "portal_membership")

        pairs = []

        for name, utility in getUtilitiesFor(ISharingPageRole):
            permission = utility.required_permission
            if permission is not None:
                if not portal_membership.checkPermission(permission, context):
                    continue
            # be friendly to utilities implemented without required_interface
            iface = getattr(utility, "required_interface", None)
            if iface is not None and not iface.providedBy(context):
                continue
            pairs.append(dict(id=name, title=utility.title))

        normalizer = getUtility(IIDNormalizer)
        pairs.sort(
            key=lambda x: normalizer.normalize(
                translate(x["title"], context=self.request)
            )
        )
        return pairs

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

        existing_settings = self.existing_role_settings()
        user_results = self.user_search_results()
        group_results = self.group_search_results()

        current_settings = existing_settings + user_results + group_results

        # We may be called when the user does a search instead of an update.
        # In that case we must not loose the changes the user made and
        # merge those into the role settings.
        requested = self.request.form.get("entries", None)
        if requested is not None:
            knownroles = [r["id"] for r in self.roles()]
            settings = {}
            for entry in requested:
                roles = [r for r in knownroles if entry.get("role_%s" % r, False)]
                settings[(entry["id"], entry["type"])] = roles

            for entry in current_settings:
                desired_roles = settings.get((entry["id"], entry["type"]), None)

                if desired_roles is None:
                    continue
                for role in entry["roles"]:
                    if entry["roles"][role] in [True, False]:
                        entry["roles"][role] = role in desired_roles

        current_settings.sort(
            key=lambda x: safe_text(x["type"]) + safe_text(x["title"])
        )

        return current_settings

    def can_edit_inherit(self):
        """If this method returns True, user can change role role inheritance status
        If it is False, inherit checkbox is not displayed on form
        """
        return True

    def inherited(self, context=None):
        """Return True if local roles are inherited here."""
        if context is None:
            context = self.context
        return not getattr(aq_base(context), "__ac_local_roles_block__", None)

    # helper functions

    @memoize
    def existing_role_settings(self):
        """Get current settings for users and groups that have already got
        at least one of the managed local roles.

        Returns a list of dicts as per role_settings()
        """
        context = self.context

        portal_membership = getToolByName(context, "portal_membership")
        portal_groups = getToolByName(context, "portal_groups")
        acl_users = getToolByName(context, "acl_users")

        info = []

        # This logic is adapted from computeRoleMap.py

        local_roles = acl_users._getLocalRolesForDisplay(context)
        acquired_roles = self._inherited_roles() + self._borg_localroles()
        available_roles = [r["id"] for r in self.roles()]

        # first process acquired roles
        items = {}
        for name, roles, rtype, rid in acquired_roles:
            items[rid] = dict(
                id=rid,
                name=name,
                type=rtype,
                sitewide=[],
                acquired=roles,
                local=[],
            )

        # second process local roles
        for name, roles, rtype, rid in local_roles:
            if rid in items:
                items[rid]["local"] = roles
            else:
                items[rid] = dict(
                    id=rid,
                    name=name,
                    type=rtype,
                    sitewide=[],
                    acquired=[],
                    local=roles,
                )

        # Make sure we always get the authenticated users virtual group
        if AUTH_GROUP not in items:
            items[AUTH_GROUP] = dict(
                id=AUTH_GROUP,
                name=_("Logged-in users"),
                type="group",
                sitewide=[],
                acquired=[],
                local=[],
            )

        # If the current user has been given roles, remove them so that he
        # doesn't accidentally lock himself out.

        member = portal_membership.getAuthenticatedMember()
        if member.getId() in items:
            items[member.getId()]["disabled"] = True

        # Sort the list: first the authenticated users virtual group, then
        # all other groups and then all users, alphabetically

        dec_users = [
            (a["id"] not in self.STICKY, a["type"], a["name"], a)
            for a in items.values()
        ]
        dec_users.sort()

        # Add the items to the info dict, assigning full name if possible.
        # Also, recut roles in the format specified in the docstring

        for d in dec_users:
            item = d[-1]
            name = item["name"]
            rid = item["id"]
            login = rid
            global_roles = set()

            if item["type"] == "user":
                member = acl_users.getUserById(rid)
                if member is not None:
                    name = (
                        member.getProperty("fullname") or member.getUserName() or name
                    )
                    global_roles = set(member.getRoles())
                    login = member.getUserName()
            elif item["type"] == "group":
                g = portal_groups.getGroupById(rid)
                name = g.getGroupTitleOrName()
                login = None
                global_roles = set(g.getRoles())

                # This isn't a proper group, so it needs special treatment :(
                if rid == AUTH_GROUP:
                    name = _("Logged-in users")

            info_item = dict(
                id=item["id"],
                type=item["type"],
                title=name,
                disabled=item.get("disabled", False),
                roles={},
            )
            if login != name:
                info_item["login"] = login

            # Record role settings
            have_roles = False
            for r in available_roles:
                if r in global_roles:
                    info_item["roles"][r] = "global"
                elif r in item["acquired"]:
                    info_item["roles"][r] = "acquired"
                    have_roles = True  # we want to show acquired roles
                elif r in item["local"]:
                    info_item["roles"][r] = True
                    have_roles = True  # at least one role is set
                else:
                    info_item["roles"][r] = False

            if have_roles or rid in self.STICKY:
                info.append(info_item)

        return info

    def _principal_search_results(
        self,
        search_for_principal,
        get_principal_by_id,
        get_principal_title,
        principal_type,
        id_key,
    ):
        """Return search results for a query to add new users or groups.

        Returns a list of dicts, as per role_settings().

        Arguments:
            search_for_principal -- a function that takes an IPASSearchView and
                a search string. Uses the former to search for the latter and
                returns the results.
            get_principal_by_id -- a function that takes a user id and returns
                the user of that id
            get_principal_title -- a function that takes a user and a default
                title and returns a human-readable title for the user. If it
                can't think of anything good, returns the default title.
            principal_type -- either 'user' or 'group', depending on what kind
                of principals you want
            id_key -- the key under which the principal id is stored in the
                dicts returned from search_for_principal
        """
        context = self.context

        translated_message = translate(
            _("Search for user or group"), context=self.request
        )
        search_term = safe_text(self.request.form.get("search_term", None))
        if not search_term or search_term == translated_message:
            return []

        existing_principals = {
            p["id"]
            for p in self.existing_role_settings()
            if p["type"] == principal_type
        }
        empty_roles = {r["id"]: False for r in self.roles()}
        info = []

        hunter = getMultiAdapter((context, self.request), name="pas_search")
        for principal_info in search_for_principal(hunter, search_term):
            principal_id = principal_info[id_key]
            if principal_id not in existing_principals:
                principal = get_principal_by_id(principal_id)
                roles = empty_roles.copy()
                if principal is None:
                    continue

                for r in principal.getRoles():
                    if r in roles:
                        roles[r] = "global"
                login = principal.getUserName()
                if principal_type == "group":
                    login = None
                info.append(
                    dict(
                        id=principal_id,
                        title=get_principal_title(principal, principal_id),
                        login=login,
                        type=principal_type,
                        roles=roles,
                    )
                )
        return info

    def user_search_results(self):
        """Return search results for a query to add new users.

        Returns a list of dicts, as per role_settings().
        """

        def search_for_principal(hunter, search_term):
            return merge_search_results(
                chain(
                    *[
                        hunter.searchUsers(**{field: search_term})
                        for field in ["name", "fullname", "email"]
                    ]
                ),
                "userid",
            )

        def get_principal_by_id(user_id):
            acl_users = getToolByName(self.context, "acl_users")
            return acl_users.getUserById(user_id)

        def get_principal_title(user, default_title):
            return user.getProperty("fullname") or user.getId() or default_title

        return self._principal_search_results(
            search_for_principal,
            get_principal_by_id,
            get_principal_title,
            "user",
            "userid",
        )

    def group_search_results(self):
        """Return search results for a query to add new groups.

        Returns a list of dicts, as per role_settings().
        """

        def search_for_principal(hunter, search_term):
            return merge_search_results(
                chain(
                    *[
                        hunter.searchGroups(**{field: search_term})
                        for field in ["id", "title"]
                    ]
                ),
                "groupid",
            )

        def get_principal_by_id(group_id):
            portal_groups = getToolByName(self.context, "portal_groups")
            return portal_groups.getGroupById(group_id)

        def get_principal_title(group, _):
            return group.getGroupTitleOrName()

        return self._principal_search_results(
            search_for_principal,
            get_principal_by_id,
            get_principal_title,
            "group",
            "groupid",
        )

    def _inherited_roles(self):
        """Returns a tuple with the acquired local roles."""
        context = self.context

        if not self.inherited(context):
            return ()

        portal = getToolByName(context, "portal_url").getPortalObject()
        result = []
        cont = True
        if portal != context:
            parent = aq_parent(context)
            while cont:
                if not getattr(parent, "acl_users", False):
                    break
                userroles = parent.acl_users._getLocalRolesForDisplay(parent)
                for user, roles, role_type, name in userroles:
                    # Find user in result
                    found = 0
                    for user2, roles2, type2, name2 in result:
                        if user2 == user:
                            # Check which roles must be added to roles2
                            for role in roles:
                                if role not in roles2:
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
        for pos in range(len(result) - 1, -1, -1):
            result[pos][1] = tuple(result[pos][1])
            result[pos] = tuple(result[pos])

        return tuple(result)

    def _borg_localroles(self):
        """Returns a tuple with roles obtained via borg.localrole adapters."""
        # Get all local roles (includeding those provided
        # by borg_localroles) and editable local roles
        # (only those stored in the object):
        pas = getToolByName(self.context, "acl_users")
        editable_local_roles = dict(self.context.get_local_roles())

        # Calculate borg_local_roles by subtracting editable local
        # roles from all available local roles (including the
        # borg.localrole provided roles):
        borg_local_roles = pas._getAllLocalRoles(self.context)
        for principal, roles in editable_local_roles.items():
            borg_local_roles[principal] = [
                r for r in borg_local_roles.get(principal, ()) if r not in roles
            ]
            if not borg_local_roles[principal]:
                del borg_local_roles[principal]

        # Adapted from: PluggableAuthService._getLocalRolesForDisplay
        result = []
        for principal, roles in borg_local_roles.items():
            username = principal
            userType = "user"
            if pas.getGroup(principal):
                userType = "group"
            else:
                user = pas.getUserById(principal)
                if user:
                    username = user.getUserName()
                    principal = user.getId()
            result.append((username, tuple(roles), userType, principal))

        return tuple(result)

    def update_inherit(self, status=True, reindex=True):
        """Enable or disable local role acquisition on the context.

        Returns True if changes were made, or False if the new settings
        are the same as the existing settings.
        """
        context = self.context
        portal_membership = getToolByName(context, "portal_membership")

        if not portal_membership.checkPermission(
            permissions.ModifyPortalContent, context
        ):
            raise Unauthorized

        block = not status
        oldblock = bool(getattr(aq_base(context), "__ac_local_roles_block__", False))

        if block == oldblock:
            return False

        if block:
            # If user has inherited local roles and removes inheritance,
            # locally set roles he inherited before
            # to avoid definitive lose of access (refs #11945)
            user = portal_membership.getAuthenticatedMember()
            context_roles = user.getRolesInContext(context)
            global_roles = user.getRoles()
            local_roles = [r for r in context_roles if r not in global_roles]
            if local_roles:
                context.manage_setLocalRoles(user.getId(), local_roles)

        context.__ac_local_roles_block__ = block and True or None
        if reindex:
            context.reindexObjectSecurity()

        return True

    @clearafter
    def update_role_settings(self, new_settings, reindex=True):
        """Update local role settings and reindex object security if necessary.

        new_settings is a list of dicts with keys id, for the user/group id;
        type, being either 'user' or 'group'; and roles, containing the list
        of role ids that are set.

        Returns True if changes were made, or False if the new settings
        are the same as the existing settings.
        """

        changed = False
        context = self.context

        managed_roles = frozenset(r["id"] for r in self.roles())
        member_ids_to_clear = []

        for s in new_settings:
            user_id = s["id"]

            existing_roles = frozenset(
                context.get_local_roles_for_userid(userid=user_id)
            )
            selected_roles = frozenset(s["roles"])

            relevant_existing_roles = managed_roles & existing_roles

            # If, for the managed roles, the new set is the same as the
            # current set we do not need to do anything.
            if relevant_existing_roles == selected_roles:
                continue

            # We will remove those roles that we are managing and which set
            # on the context, but which were not selected
            to_remove = relevant_existing_roles - selected_roles

            # Leaving us with the selected roles, less any roles that we
            # want to remove
            wanted_roles = (selected_roles | existing_roles) - to_remove

            # take away roles that we are managing, that were not selected
            # and which were part of the existing roles

            if wanted_roles:
                context.manage_setLocalRoles(user_id, list(wanted_roles))
                changed = True
            elif existing_roles:
                member_ids_to_clear.append(user_id)

        if member_ids_to_clear:
            context.manage_delLocalRoles(userids=member_ids_to_clear)
            changed = True

        if changed and reindex:
            self.context.reindexObjectSecurity()

        return changed

    def updateSharingInfo(self, search_term=""):
        self.handle_form()
        the_id = "user-group-sharing"
        macro = self.template.macros[the_id]
        res = self.macro_wrapper(the_macro=macro, instance=self.context, view=self)
        messages = self.context.restrictedTraverse("global_statusmessage")()
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({"body": res, "messages": messages})
