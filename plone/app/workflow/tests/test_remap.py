from plone.app.testing import login
from plone.app.workflow.remap import remap_workflow
from plone.app.workflow.testing import PLONE_APP_WORKFLOW_INTEGRATION_TESTING

import unittest


class TestRemapWorkflow(unittest.TestCase):

    layer = PLONE_APP_WORKFLOW_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        login(self.portal, "manager")

        self.workflow.setChainForPortalTypes(
            ("Document",),
            ("simple_publication_workflow",),
        )
        self.workflow.setChainForPortalTypes(
            ("News Item",),
            ("one_state_workflow",),
        )
        self.workflow.setChainForPortalTypes(("Folder",), ())
        self.workflow.setChainForPortalTypes(("Image",), None)

        self.portal.invokeFactory("Document", "d1")
        self.portal.invokeFactory("Document", "d2")
        self.portal.invokeFactory("News Item", "n1")
        self.portal.invokeFactory("Image", "i1")

        self.workflow.doActionFor(self.portal.d1, "publish")

    def _state(self, obj):
        return self.workflow.getInfoFor(obj, "review_state")

    def _chain(self, obj):
        return self.workflow.getChainFor(obj)

    def test_remap_multiple_no_state_map(self):
        remap_workflow(
            self.portal,
            type_ids=(
                "Document",
                "News Item",
            ),
            chain=("plone_workflow",),
        )

        self.assertEqual(self._chain(self.portal.d1), ("plone_workflow",))
        self.assertEqual(self._chain(self.portal.d2), ("plone_workflow",))
        self.assertEqual(self._chain(self.portal.n1), ("plone_workflow",))

        self.assertEqual(self._state(self.portal.d1), "visible")
        self.assertEqual(self._state(self.portal.d2), "visible")
        self.assertEqual(self._state(self.portal.n1), "visible")

    def test_remap_with_partial_state_map(self):
        remap_workflow(
            self.portal,
            type_ids=(
                "Document",
                "News Item",
            ),
            chain=("plone_workflow",),
            state_map={"published": "published"},
        )

        self.assertEqual(self._chain(self.portal.d1), ("plone_workflow",))
        self.assertEqual(self._chain(self.portal.d2), ("plone_workflow",))
        self.assertEqual(self._chain(self.portal.n1), ("plone_workflow",))

        self.assertEqual(self._state(self.portal.d1), "published")
        self.assertEqual(self._state(self.portal.d2), "visible")
        self.assertEqual(self._state(self.portal.n1), "published")

    def test_remap_to_no_workflow(self):
        view_at_d1 = [
            r["name"] for r in self.portal.d1.rolesOfPermission("View") if r["selected"]
        ]
        self.assertIn("Anonymous", view_at_d1)

        remap_workflow(
            self.portal,
            type_ids=(
                "Document",
                "News Item",
            ),
            chain=(),
        )

        self.assertEqual(self._chain(self.portal.d1), ())
        self.assertEqual(self._chain(self.portal.d2), ())
        self.assertEqual(self._chain(self.portal.n1), ())

        view_at_d1 = [
            r["name"] for r in self.portal.d1.rolesOfPermission("View") if r["selected"]
        ]
        self.assertFalse("Anonymous" in view_at_d1)
        self.assertTrue(self.portal.d1.acquiredRolesAreUsedBy("View"))

    def test_remap_from_no_workflow(self):
        remap_workflow(
            self.portal,
            type_ids=("Image",),
            chain=("plone_workflow",),
        )

        self.assertEqual(self._chain(self.portal.i1), ("plone_workflow",))
        self.assertEqual(self._state(self.portal.i1), "visible")

    def test_remap_to_default(self):
        self.workflow.setDefaultChain("plone_workflow")
        remap_workflow(
            self.portal,
            type_ids=("Image",),
            chain="(Default)",
        )

        self.assertEqual(self._chain(self.portal.i1), ("plone_workflow",))
