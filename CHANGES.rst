Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

5.0.0a2 (2021-09-15)
--------------------

Bug fixes:


- Remove cyclic dependency with Products.CMFPlone
  [sneridagh] (#30)


5.0.0a1 (2021-04-21)
--------------------

Breaking changes:


- Update for Plone 6 with Bootstrap markup
  [petschki, agitator] (#29)


New features:


- Have the icons from the sharing tab to have their URL relative to the site root
  [frapell] (#25)


4.0.3 (2020-09-26)
------------------

Bug fixes:


- Fixed deprecation warning for ``zope.component.interfaces.IComponentRegistry``.
  Fixed deprecation warning for zope.site.hooks.
  [maurits] (#3130)


4.0.2 (2020-04-20)
------------------

Bug fixes:


- Minor packaging updates. (#1)


4.0.1 (2019-03-03)
------------------

Bug fixes:


- The sharing search form remembers the search term [ale-rt] (#19)


4.0.0 (2018-11-02)
------------------

Breaking changes:

- No need to define cmf.ChangeLocalRoles in zcml since this is in by Products.CMFCore>=2.4.0b2
  [jensens]

- Adapt tests to `Products.GenericSetup >= 2.0` thus requiring at least that
  version.
  [jessesnyder]

New features:

- Replaced usages of my_worklist.py skin script.
  https://github.com/plone/Products.CMFPlone/issues/1801
  [reinhardt]

- Python3 compatibility
  [jessesnyder, pbauer]

Bug fixes:

- Update tests to use testing best practices (and stop using the bbb module from p.a.testing).
  [gforcada]


3.0 (2017-05-29)
----------------

Breaking changes:

- Removed long time deprecated and unused permission "Change portal events".
  [kakshay21]


2.2.7 (2017-02-12)
------------------

Bug fixes:

- Fixed test failure for LookupError, having extra 'available items' (Zope 4)
  [davisagli]


2.2.6 (2016-08-18)
------------------

Bug fixes:

- Use zope.interface decorator.
  [gforcada]


2.2.5 (2016-05-15)
------------------

New:

- Add a direct link from a group name on Sharing ab to that group's
  member list for users with sufficient permissions [PLIP #1310]
  [datakurre]


2.2.4 (2015-09-20)
------------------

- Use safe_unicode for search in @@sharing.
  Fixes https://github.com/plone/Products.CMFPlone/issues/930
  [pbauer]


2.2.3 (2015-03-22)
------------------

- Remove DL's from portal message in templates.
  [khink]


2.2.2 (2014-10-23)
------------------

- Show login-name even if it is the same as the user-id.
  Fixes https://dev.plone.org/ticket/14259
  [pbauer]


2.2.1 (2014-04-13)
------------------

- Introduce ``plone.app.workflow.interfaces.ILocalrolesModifiedEvent``.
  ``LocalrolesModifiedEvent`` gets fired after local roles have been changed.
  [rnix]

- Introduce ``required_interface`` attribute on
  ``plone.app.workflow.interfaces.ISharingPageRole``.
  [rnix]


2.2.0 (2014-02-23)
------------------

- Remove DL's from portal message in templates.
  https://github.com/plone/Products.CMFPlone/issues/153
  [khink]

- Replace deprecated test assert statements.
  [timo]

- Show user's login name instead of the user id, which is an internal
  identifier.
  [davisagli]

- Include roles derived from borg.localrole adapters on the Sharing tab,
  appearing as inherited roles.
  [datakurre, davisagli]


2.1.3 (2013-04-29)
------------------

- Add json header to sharing.py.
  [travacic]


2.1.2 (2013-01-13)
------------------

- Call searchUsers with the 'name' argument instead of 'login'.
  'name' is the officially supported way according to the PAS interface.
  [maurits]


2.1.1 (2013-01-01)
------------------

- Extensibility improvement on sharing view so developers can easily
  override this view and change what groups are always displayed (STICKY).
  [ispburger]

- Use HTML5 placeholder attribute on Sharing tab search box. Replaces
  deprecated inputLabel class.
  [danjacka]


2.1.0 (2012-10-16)
------------------

- Remove kss. JS integration is in Products.CMFPlone.
  [vangheem]


2.0.8 (2012-10-03)
------------------

- Refactor: we can easily customize the sharing view
  so that add/remove inherit field is removed.
  [thomasdesvenain]

- Search on email address within the Sharing view.
  [davidjb]


2.0.7 (2012-06-29)
------------------

- Don't use deprecated .gif icons.
  [davisagli]


2.0.6 (2011-11-24)
------------------

- Avoid failure if user with global 'Manager' role
  removes inheritance on sharing.
  [thomasdesvenain]

- Ensure a stable ordering in the sharing.xml GS export.
  [hannosch]


2.0.5 (2011-08-31)
------------------

- User should click the 'Save' button to actually save its changes in the
  sharing tab. IOW we dont want to update local roles while searching
  for users.
  [jfroche]


2.0.4 - 2011-07-04
------------------

- If user has inherited local roles on a folder and removes inheritance on
  sharing page, locally set roles that were inherited before to avoid
  definitive loss of access.
  This refs http://dev.plone.org/plone/ticket/11945.
  [thomasdesvenain]

- In sharing view, return empty list immediately if search_term is the
  translated "Search for user or group" message.
  [vincentfretin]

- In sharing view, the search for users and groups was done twice, once in
  macro_wrapper template and another one in the user-group-sharing macro
  in sharing template because of duplicate variable definitions.
  [vincentfretin]


2.0.3 - 2011-05-12
------------------

- Add MANIFEST.in.
  [WouterVH]

- Normalize translated string before sorting sharing columns.
  [vincentfretin]


2.0.2 - 2011-04-03
------------------

- Sort sharing columns by translated title instead of role id.
  [vincentfretin]

- Added plone.abovecontentbody viewletmanager in sharing view.
  [vincentfretin]


2.0.1 - 2011-01-04
------------------

- Depend on ``Products.CMFPlone`` instead of ``Plone``.
  [elro]

- Add Site Administrator to the roles which are allowed to delegate the other
  roles (for forward compatibility with Plone 4.1).
  [davisagli]

- Sharing table is into a div container.
  [thomasdesvenain]


2.0 - 2010-07-18
----------------

- Update license to GPL version 2 only.
  [hannosch]


2.0b2 - 2010-03-05
------------------

- Adapt tests to new policy introduced in
  http://dev.plone.org/plone/changeset/34375
  References http://dev.plone.org/plone/ticket/10236
  [tomster]


2.0b1 - 2010-02-18
------------------

- Updated sharing.pt to the recent markup conventions.
  References http://dev.plone.org/plone/ticket/9981
  [spliter]

- Allow @@sharing to search for group title as well as id.
  Closes http://dev.plone.org/plone/ticket/9269
  [esteele]


2.0a3 - 2009-12-27
------------------

- Add support for GenericSetup roles removal in sharing.xml. This
  closes http://dev.plone.org/plone/ticket/9979.
  [dukebody, thanks optilude]

- Use zope.site and declare missing package dependencies.
  [hannosch]


2.0a2 - 2009-12-16
------------------

- Changed msgid box_search to label_search in sharing.pt. box_search have
  a different semantic in the header for the rendered search portlet.
  This closes http://dev.plone.org/plone/ticket/9752

- Don't include <q> tag in heading_currently_assigned_shares message.
  [vincentfretin]


2.0a1 - 2009-11-14
------------------

- Specify complete package dependencies and some cleanups.
  [hannosch]

- Changed default message from "User/Group" to "Name" for
  label_name msgid in sharing.pt.
  [vincentfretin]

- Added support for the sharing.xml import/export syntax.
  [optilude]


1.2 - 2009-05-10
----------------

- Use our own PloneMessageFactory.
  [hannosch]

- Fixed deprecation warnings for use of Globals.
  [hannosch]

- Specified package dependencies.
  [hannosch]

- Display the userid in addition to the fullname if they are different.
  Fixes http://dev.plone.org/plone/ticket/8251.
  [csenger]

- Adjusted a test to work with Zope 2.12.
  [hannosch]

- Use safe_unicode() instead of str() to fix #7576. Fixes
  http://dev.plone.org/plone/ticket/8371.
  [csenger]


1.1.5 - 2008-08-18
------------------

- Correct UnicodeDecodeError in sharing-view when users or groups with
  non-ascii characters are searched. All parameters fetched from the
  request are strings, but _(u'Logged-in users') isn't. A string with
  non-ascii characters and a unicode-string can't be joined. Fixes
  http://dev.plone.org/plone/ticket/7576
  [csenger]


1.1.4 - 2008-07-24
------------------

- Keep the icons for inherited and global roles when updating the sharing
  page after a search. This fixes http://dev.plone.org/plone/ticket/8313 .
  [wichert]

- Sort the principals in the sharing page. Before they could reorder
  randomly when saving changes.
  [wichert]

- Fix a logic error in sharing page view: role changes would appear to be
  lost when saving a view, while the were really applied. This fixes
  http://dev.plone.org/plone/ticket/8295 .
  [wichert]


1.1.3 - 2008-07-07
------------------

- Modify the inline (kss) search option in the sharing page to only search
  and not update the roles and search. This behaviour was unintuitive and
  possible very very slow.
  [wichert]

- Update the sharing page to do nothing if the new set of roles is the
  same as the current set of roles.
  [wichert]

- Update sharing code to only reindex once instead of twice.
  [wichert]

- Only call reindexObjectSecurity from the sharing tab's update_inherit method
  if the setting actually changed.  This avoids an unnecessary, potentially
  expensive catalog reindex in many cases.
  [davisagli]

- Update the search-result merging code based on the code from PlonePAS 3.6.
  [wichert]

- Handle principals which can not be retrieved. This can occur in LDAP
  environments.
  [wichert]

- Mark the security names as public so they can be imported everywhere
  and register them with Zope on startup so you can manage them via the
  ZMI or a GenericSetup profile.
  [wichert]


1.1.0 - 2008-04-21
------------------

- Protect the "sharing" form against CSRF attacks.
  [witsch]


1.0.7 - 2008-03-09
------------------

- Created fine-grained permissions for delegating sharing page roles in
  order to avoid people with a delegated permission escalating their own
  privileges. This can now be controlled at a high level by the
  "Sharing page: Delegate roles" permission, which controls access to the
  Sharing page machinery, and at an individual roles basis, with
  permissions like "Sharing page: Delegate Editor role".
  http://dev.plone.org/plone/ticket/7652

- Stopped people from locking themselves out by disabling the ability
  to edit their own roles.

- Added friendly "Changes saved" message.
  http://dev.plone.org/plone/ticket/6966

- user_search_results() now searches in login name as well as fullname.
  Fixes http://dev.plone.org/plone/ticket/6853
  [erikrose]

- Factored up the duplicated logic from user_search_results() and
  group_search_results() to form _principal_search_results().
  [erikrose]


0.1
---

- Added missing closing head tag to sharing.pt. This closes
  http://dev.plone.org/plone/ticket/7161.
  [hannosch]
