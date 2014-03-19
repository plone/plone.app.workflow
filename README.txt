Introduction
============

``plone.app.workflow`` contains workflow- and security-related features for
Plone, including the sharing view.


Generic Setup
-------------

This package supports the GenericSetup syntax to add new roles to the "Sharing"
page. Local roles are defined in ``sharing.xml`` and looks as follows::

  <sharing xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="plone">
      <role
          id="CopyEditor"
          title="Can edit copy"
          permission="Manage portal"
          interface="Products.CMFPlone.interfaces.ISiteRoot"
          i18n:attributes="title"
          />
  </sharing>

``id`` and ``title`` are mandatory, while ``permission`` and ``interface`` are
optional.

The ``permission`` attribute defines which permission is required in order to
display the related role in the sharing form.

The ``interface`` attribute declares the required interface a context must
implement in order to display the related role in the sharing form.


Event notification
------------------

This package introduces ``ILocalrolesModifiedEvent`` which derives from
``zope.lifecycleevent.IModifiedEvent``. The concrete
``LocalrolesModifiedEvent`` gets fired after local roles have been modified and
after object security has been reindexed.
