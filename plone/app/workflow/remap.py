import transaction
from zope.component import getUtility

from DateTime import DateTime

from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.interfaces import IConfigurableWorkflowTool

SAVE_THRESHOLD = 100 # Do a savepoint every so often
_marker = object()


def remap_workflow(context, type_ids, chain, state_map={}):
    """Change the workflow for each type in type_ids to use the workflow
    chain given. state_map is a dictionary of old state names to
    new ones. States that are not found will be remapped to the default
    state of the new workflow.
    """
    
    portal_workflow = getUtility(IConfigurableWorkflowTool)
    
    default_chain = portal_workflow.getDefaultChain()
    chains_by_type = dict(portal_workflow.listChainOverrides())
    
    # Build a dictionary of type id -> chain before we made changes
    old_chains = dict([(t, chains_by_type.get(t, default_chain)) for t in type_ids])

    # Update the workflow chain in portal_workflows.
    portal_workflow.setChainForPortalTypes(type_ids, chain)

    # If we were setting to the "no workflow" chain, there are no updates
    # to be made. Security will be left as it was.
    if chain is not None and len(chain) == 0:
        return
    
    # Otherwise, we need to remap
    
    chain_workflows = {}
    if chain is not None:
        for c in chain:
            chain_workflows[c] = getattr(portal_workflow, c)
    for oc in old_chains.values():
        for c in oc:
            if c not in chain_workflows:
                chain_workflows[c] = getattr(portal_workflow, c)
    
    target_chain = chain
    if target_chain is None:
        target_chain = default_chain
    
    portal_catalog = getUtility(ICatalogTool)
    
    # Then update the state of each
    remapped_count = 0
    threshold_count = 0
    for brain in portal_catalog(portal_type=type_ids):
        obj = brain.getObject()
        
        # Work out what, if any, the previous state of the object was
        portal_type = brain.portal_type
        old_chain = old_chains[portal_type]
        old_wf = None
        if len(old_chain) > 0:
            old_wf = chain_workflows[old_chain[0]]
        
        old_state = None
        if old_wf is not None:
            old_status = portal_workflow.getStatusOf(old_wf.getId(), obj)
            if old_status is not None:
                old_state = old_status.get('review_state', None)
            
        # Now add a transition
        for new_wf_name in target_chain:
            new_wf = chain_workflows[new_wf_name]
            new_status = { 'action'       : None,
                           'actor'        : None, 
                           'comments'     : 'State remapped from control panel',
                           'review_state' : state_map.get(old_state, new_wf.initial_state),
                           'time'         : DateTime()}
            portal_workflow.setStatusOf(new_wf_name, obj, new_status)
            
            # Trigger any automatic transitions, or else just make sure the role mappings are right
            auto_transition = new_wf._findAutomaticTransition(obj, new_wf._getWorkflowStateOf(obj))
            if auto_transition is not None:
                new_wf._changeStateOf(obj, auto_transition)
            else:
                new_wf.updateRoleMappingsFor(obj)

        obj.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
        
        remapped_count += 1
        threshold_count += 1
        
        if threshold_count > SAVE_THRESHOLD:
            transaction.savepoint()
            threshold_count = 0
            
    return remapped_count