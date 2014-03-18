Introduction
============

plone.app.workflow contains workflow- and security-related features for Plone,
including the sharing view.

It also supports the `sharing.xml` GenericSetup syntax, to add new roles to
the "Sharing" page::

  <sharing xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="plone">
      <role
          id="CopyEditor"
          title="Can edit copy"
          permission="Manage portal"
          interface="Products.CMFPlone.interfaces.ISiteRoot"
          i18n:attributes="title"
          />
  </sharing>

The `interface` attribute is optional. It declares the required interface a
context must implement, so that the given role is displayed in the sharing tab.
