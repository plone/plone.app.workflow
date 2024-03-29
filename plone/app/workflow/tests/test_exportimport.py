from five.localsitemanager import make_objectmanager_site
from OFS.Folder import Folder
from plone.app.workflow.exportimport import export_sharing
from plone.app.workflow.exportimport import import_sharing
from plone.app.workflow.exportimport import PersistentSharingPageRole
from plone.app.workflow.exportimport import SharingXMLAdapter
from plone.app.workflow.interfaces import ISharingPageRole
from plone.testing.zca import UNIT_TESTING
from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import DummyImportContext
from zope.component import getSiteManager
from zope.component import getUtilitiesFor
from zope.component import provideAdapter
from zope.component import provideUtility
from zope.component.hooks import clearSite
from zope.component.hooks import setHooks
from zope.component.hooks import setSite
from zope.interface import Interface

import unittest


class ExportImportTest(unittest.TestCase):
    layer = UNIT_TESTING

    def setUp(self):
        provideAdapter(SharingXMLAdapter, name="plone.app.workflow.sharing")

        site = Folder("plone")
        make_objectmanager_site(site)
        setHooks()
        setSite(site)
        sm = getSiteManager()

        self.site = site
        self.sm = sm

    def roles(self):
        return dict(getUtilitiesFor(ISharingPageRole))

    def tearDown(self):
        clearSite()


class TestImport(ExportImportTest):
    def test_empty_import_no_purge(self):
        xml = "<sharing />"
        context = DummyImportContext(self.site, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)

        self.assertEqual(0, len(self.roles()))

    def test_import_single_no_purge(self):
        xml = """\
<sharing>
    <role id='CopyEditor'
          title='Can copyedit'
          permission='Delegate edit copy'
          interface='zope.interface.Interface' />
</sharing>
"""
        context = DummyImportContext(self.site, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(1, len(roles))

        self.assertEqual("Can copyedit", roles["CopyEditor"].title)
        self.assertEqual("Delegate edit copy", roles["CopyEditor"].required_permission)
        self.assertEqual(Interface, roles["CopyEditor"].required_interface)

    def test_import_multiple_no_purge(self):
        xml = """\
<sharing>
    <role id='CopyEditor'
          title='Can copyedit'
          permission='Delegate edit copy'
          interface='zope.interface.Interface' />
    <role id='Controller'
          title='Can control' />
</sharing>
"""
        context = DummyImportContext(self.site, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(2, len(roles))
        self.assertEqual("Can copyedit", roles["CopyEditor"].title)
        self.assertEqual("Delegate edit copy", roles["CopyEditor"].required_permission)
        self.assertEqual(Interface, roles["CopyEditor"].required_interface)
        self.assertEqual("Can control", roles["Controller"].title)
        self.assertEqual(None, roles["Controller"].required_permission)

    def test_import_multiple_times_no_purge(self):
        xml = """\
<sharing>
    <role id='CopyEditor'
          title='Can copyedit'
          permission='Delegate edit copy'
          interface='zope.interface.Interface' />
</sharing>
"""
        context = DummyImportContext(self.site, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(1, len(roles))
        self.assertEqual("Can copyedit", roles["CopyEditor"].title)
        self.assertEqual("Delegate edit copy", roles["CopyEditor"].required_permission)
        self.assertEqual(Interface, roles["CopyEditor"].required_interface)

        xml = """\
<sharing>
    <role id='Controller'
          title='Can control' />
</sharing>
"""
        context = DummyImportContext(self.site, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(2, len(roles))
        self.assertEqual("Can copyedit", roles["CopyEditor"].title)
        self.assertEqual("Delegate edit copy", roles["CopyEditor"].required_permission)
        self.assertEqual(Interface, roles["CopyEditor"].required_interface)
        self.assertEqual("Can control", roles["Controller"].title)
        self.assertEqual(None, roles["Controller"].required_permission)

    def test_import_multiples_times_purge(self):
        xml = """\
<sharing>
    <role id='CopyEditor'
          title='Can copyedit'
          permission='Delegate edit copy'
          interface='zope.interface.Interface' />
</sharing>
"""
        context = DummyImportContext(self.site, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(1, len(roles))
        self.assertEqual("Can copyedit", roles["CopyEditor"].title)
        self.assertEqual("Delegate edit copy", roles["CopyEditor"].required_permission)
        self.assertEqual(Interface, roles["CopyEditor"].required_interface)

        xml = """\
<sharing>
    <role id='Controller'
          title='Can control' />
</sharing>
"""
        context = DummyImportContext(self.site, purge=True)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(1, len(roles))
        self.assertEqual("Can control", roles["Controller"].title)
        self.assertEqual(None, roles["Controller"].required_permission)

    def test_import_multiples_times_no_purge_overwrite(self):
        xml = """\
<sharing>
    <role id='CopyEditor'
          title='Can copyedit'
          permission='Delegate edit copy'
          interface='zope.interface.Interface' />
</sharing>
"""
        context = DummyImportContext(self.site, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(1, len(roles))
        self.assertEqual("Can copyedit", roles["CopyEditor"].title)
        self.assertEqual("Delegate edit copy", roles["CopyEditor"].required_permission)
        self.assertEqual(Interface, roles["CopyEditor"].required_interface)

        xml = """\
<sharing>
    <role id='CopyEditor'
          title='Can edit copy'
          permission='Delegate: CopyEditor' />
</sharing>
"""
        context = DummyImportContext(self.site, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(1, len(roles))
        self.assertEqual("Can edit copy", roles["CopyEditor"].title)
        self.assertEqual(
            "Delegate: CopyEditor", roles["CopyEditor"].required_permission
        )
        self.assertEqual(None, roles["CopyEditor"].required_interface)

    def test_import_override_global(self):
        provideUtility(
            PersistentSharingPageRole("Do stuff", "A permission"),
            ISharingPageRole,
            name="DoerOfStuff",
        )

        xml = """\
<sharing>
    <role id='CopyEditor'
          title='Can copyedit'
          permission='Delegate edit copy' />
    <role id='DoerOfStuff'
          title='Can do stuff'
          permission='Delegate doing stuff' />
</sharing>
"""
        context = DummyImportContext(self.site, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(2, len(roles))
        self.assertEqual("Can copyedit", roles["CopyEditor"].title)
        self.assertEqual("Delegate edit copy", roles["CopyEditor"].required_permission)
        self.assertEqual(None, roles["CopyEditor"].required_interface)
        self.assertEqual("Can do stuff", roles["DoerOfStuff"].title)
        self.assertEqual(
            "Delegate doing stuff", roles["DoerOfStuff"].required_permission
        )

    def test_remove_one(self):
        xml = """\
<sharing>
    <role id='CopyEditor'
          title='Can copyedit'
          permission='Delegate edit copy' />
</sharing>
"""
        context = DummyImportContext(self.sm, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(1, len(roles))
        self.assertEqual("Can copyedit", roles["CopyEditor"].title)

        xml = """\
<sharing>
    <role remove="True"
          id='CopyEditor' />
</sharing>
"""
        context = DummyImportContext(self.sm, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(0, len(roles))

    def test_remove_multiple(self):
        xml = """\
<sharing>
    <role id='CopyEditor'
          title='Can copyedit'
          permission='Delegate edit copy' />
    <role id='DoerOfStuff'
          title='Can do stuff'
          permission='Delegate doing stuff' />
</sharing>
"""
        context = DummyImportContext(self.sm, purge=False)
        context._files = {"sharing.xml": xml}
        import_sharing(context)

        xml = """\
<sharing>
    <role id='Hacker'
          title='Can hack'
          permission='Hack the system' />
    <role remove="True"
          id='CopyEditor'
          title='Can copyedit'
          permission='Delegate edit copy' />
</sharing>
"""
        context = DummyImportContext(self.sm, purge=False)
        context._files = {"sharing.xml": xml}

        import_sharing(context)
        roles = self.roles()

        self.assertEqual(2, len(roles))
        self.assertEqual("Can do stuff", roles["DoerOfStuff"].title)
        self.assertEqual("Can hack", roles["Hacker"].title)


class TestExport(ExportImportTest):
    def test_export_empty(self):
        xml = b"""\
<?xml version="1.0" encoding="utf-8"?>
<sharing/>
"""
        context = DummyExportContext(self.site)
        export_sharing(context)

        self.assertEqual("sharing.xml", context._wrote[0][0])
        self.assertEqual(xml, context._wrote[0][1])

    def test_export_multiple(self):
        sm = self.site.getSiteManager()

        # Will not be exported, as it's global
        provideUtility(
            PersistentSharingPageRole("Do stuff", "A permission"),
            ISharingPageRole,
            name="DoerOfStuff",
        )

        # Will not be exported, as it wasn't imported with this handler
        sm.registerUtility(
            PersistentSharingPageRole("Do other Stuff"),
            ISharingPageRole,
            "DoerOfOtherStuff",
        )

        import_xml = b"""\
<sharing>
 <role title="Can control" id="Controller"/>
 <role title="Can copyedit" id="CopyEditor"
    interface="zope.interface.Interface" permission="Delegate edit copy"/>
</sharing>
"""

        export_xml = b"""\
<?xml version="1.0" encoding="utf-8"?>
<sharing>
 <role title="Can control" id="Controller"/>
 <role title="Can copyedit" id="CopyEditor"
    interface="zope.interface.Interface" permission="Delegate edit copy"/>
</sharing>
"""

        import_context = DummyImportContext(self.site, purge=False)
        import_context._files = {"sharing.xml": import_xml}

        import_sharing(import_context)

        export_context = DummyExportContext(self.site)
        export_sharing(export_context)

        self.assertEqual("sharing.xml", export_context._wrote[0][0])

        self.assertEqual(export_xml, export_context._wrote[0][1])
