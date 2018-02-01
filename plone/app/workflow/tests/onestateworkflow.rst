=======================================================
Functional Testing of the One State Workflow Definition
=======================================================

First, some set-up of our site for testing:

    >>> from plone.testing.z2 import Browser

    >>> app = layer['app']
    >>> portal = layer['portal']
    >>> request = layer['request']

    >>> portal_workflow = portal.portal_workflow
    >>> portal_url = portal.absolute_url()
    >>> folder_url = '%s/folder1' % portal_url
    >>> document_url = '%s/folder1/document1' % portal_url

    >>> browser = Browser(app)

Verify that our items are actually all in the one_state_workflow and in our
default 'published' state

    >>> portal_workflow.getChainForPortalType('Document')
    ('one_state_workflow',)
    >>> portal_workflow.getChainForPortalType('Folder')
    ('one_state_workflow',)
    >>> portal_workflow.getChainForPortalType('News Item')
    ('one_state_workflow',)
    >>> portal_workflow.getChainForPortalType('Event')
    ('one_state_workflow',)

    >>> portal_workflow.getInfoFor(portal.folder1, 'review_state')
    'published'
    >>> portal_workflow.getInfoFor(portal.folder1.document1, 'review_state')
    'published'
    >>> portal_workflow.getInfoFor(portal.folder1.newsitem1, 'review_state')
    'published'


Test as anonymous
-----------------

XXX - Test this logout by outputting the HTML to make sure we're actually anon
here

Now we logout, so that we can inspect our item as an anonymous user

    >>> browser.open('%s/logout' % portal_url)

Head over to our temporary folder containing our one_state_workflow items

    >>> browser.open(folder_url)

We're not forced to log in and we can view the item. Thus, we have view permission

    >>> 'Login Name' not in browser.contents
    True

We can also access contents information

    >>> 'document1' and 'newsitem1' in browser.contents
    True

We shouldn't see the edit tab

    >>> browser.getControl('Edit')
    Traceback (most recent call last):
    ...
    LookupError: label 'Edit'...
    >>> browser.open(document_url)
    >>> browser.getControl('Edit')
    Traceback (most recent call last):
    ...
    LookupError: label 'Edit'...

Or have the "Modify portal content" permission in any scenario

    >>> browser.open('%s/edit' % folder_url)
    >>> 'Login Name' in browser.contents
    True

    >>> browser.open('%s/edit' % document_url)
    >>> 'Login Name' in browser.contents
    True


Test with the member role
-------------------------
Logout, so that we can inspect our item as another user of the system

    >>> browser.open('%s/logout' % portal_url)
    >>> browser.open('%s/login_form' % portal_url)
    >>> browser.getControl(name='__ac_name').value = 'member'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl('Log in').click()

Head over to our temporary folder containing our one_state_workflow items

    >>> browser.open(folder_url)

We're not forced to log in and we can view the item. Thus, we have view permission

    >>> 'Login Name' not in browser.contents
    True

We can also access contents information

    >>> 'document1' and 'newsitem1' in browser.contents
    True

We shouldn't see the edit tab

    >>> browser.getControl('Edit')
    Traceback (most recent call last):
    ...
    LookupError: label 'Edit'...
    >>> browser.open(document_url)
    >>> browser.getControl('Edit')
    Traceback (most recent call last):
    ...
    LookupError: label 'Edit'...

Or have the "Modify portal content" permission in any scenario

    >>> # browser.open('%s/edit' % self.folder.absolute_url())
