#
# Tests the remap-workflow functionality
#

from base import WorkflowTestCase
from plone.app.workflow.remap import remap_workflow


class TestRemapWorkflow(WorkflowTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
    
        self.setRoles(('Manager',))
    
        self.workflow.setChainForPortalTypes(('Document','Event',), ('simple_publication_workflow',))
        self.workflow.setChainForPortalTypes(('News Item',), ('one_state_workflow',))
        self.workflow.setChainForPortalTypes(('Folder',), ())
        self.workflow.setChainForPortalTypes(('Image',), None)
        
        self.portal.invokeFactory('Document', 'd1')
        self.portal.invokeFactory('Document', 'd2')
        self.folder.invokeFactory('Event', 'e1')
        self.folder.invokeFactory('Document', 'e2')
        self.portal.invokeFactory('News Item', 'n1')
        self.portal.invokeFactory('Image', 'i1')

        self.workflow.doActionFor(self.portal.d1, 'publish')

    def _state(self, obj):
        return self.workflow.getInfoFor(obj, 'review_state')

    def _chain(self, obj):
        return self.workflow.getChainFor(obj)

    def test_remap_multiple_no_state_map(self):
        remap_workflow(self.portal, 
                       type_ids=('Document','News Item',), 
                       chain=('community_workflow',))
                       
        self.assertEquals(self._chain(self.portal.d1), ('community_workflow',))
        self.assertEquals(self._chain(self.portal.d2), ('community_workflow',))
        self.assertEquals(self._chain(self.portal.n1), ('community_workflow',))
                       
        self.assertEquals(self._state(self.portal.d1), 'public_draft')
        self.assertEquals(self._state(self.portal.d2), 'public_draft')
        self.assertEquals(self._state(self.portal.n1), 'public_draft')
        
    def test_remap_with_partial_state_map(self):
        remap_workflow(self.portal, 
                       type_ids=('Document','News Item',), 
                       chain=('community_workflow',),
                       state_map={'published' : 'published'})
                       
        self.assertEquals(self._chain(self.portal.d1), ('community_workflow',))
        self.assertEquals(self._chain(self.portal.d2), ('community_workflow',))
        self.assertEquals(self._chain(self.portal.n1), ('community_workflow',))
                       
        self.assertEquals(self._state(self.portal.d1), 'published')
        self.assertEquals(self._state(self.portal.d2), 'public_draft')
        self.assertEquals(self._state(self.portal.n1), 'published')
        
    def test_remap_to_no_workflow(self):
        remap_workflow(self.portal, 
                       type_ids=('Document','News Item',), 
                       chain=())
                       
        self.assertEquals(self._chain(self.portal.d1), ())
        self.assertEquals(self._chain(self.portal.d2), ())
        self.assertEquals(self._chain(self.portal.n1), ())
        
        
    def test_remap_from_no_workflow(self):
        remap_workflow(self.portal, 
                       type_ids=('Image',), 
                       chain=('community_workflow',))
                       
        self.assertEquals(self._chain(self.portal.i1), ('community_workflow',))
        self.assertEquals(self._state(self.portal.i1), 'public_draft')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRemapWorkflow))
    return suite
