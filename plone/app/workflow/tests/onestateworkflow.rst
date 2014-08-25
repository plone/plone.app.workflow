=======================================================
Functional Testing of the One State Workflow Definition
=======================================================

First, some set-up of our site for testing:

    >>> self.setUpDefaultWorkflow(defaultWorkflow='one_state_workflow')

    >>> from plone.testing.z2 import Browser
    >>> browser = Browser(app)

Let us log all exceptions, which is useful for debugging.

    >>> self.portal.error_log._ignored_exceptions = ()
    >>> import transaction; transaction.commit()

Verify that our items are actually all in the one_state_workflow and in our
default 'published' state

    >>> self.workflow.getChainForPortalType('Document')
    ('one_state_workflow',)
    >>> self.workflow.getChainForPortalType('Folder')
    ('one_state_workflow',)
    >>> self.workflow.getChainForPortalType('News Item')
    ('one_state_workflow',)
    >>> self.workflow.getChainForPortalType('Event')
    ('one_state_workflow',)

    >>> self.workflow.getInfoFor(self.folder, 'review_state')
    'published'
    >>> self.workflow.getInfoFor(self.folder.document1, 'review_state')
    'published'
    >>> self.workflow.getInfoFor(self.folder.newsitem1, 'review_state')
    'published'


Test as anonymous
-----------------

XXX - Test this logout by outputting the HTML to make sure we're actually anon
here

Now we logout, so that we can inspect our item as an anonymous user

    >>> browser.open('%s/logout' % self.portal.absolute_url())

Head over to our temporary folder containing our one_state_workflow items

    >>> browser.open('%s' % self.folder.absolute_url())

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
    LookupError: label 'Edit'
    >>> browser.open('%s' % self.folder.document1.absolute_url())
    >>> browser.getControl('Edit')
    Traceback (most recent call last):
    ...
    LookupError: label 'Edit'

Or have the "Modify portal content" permission in any scenario

    >>> browser.open('%s/edit' % self.folder.absolute_url())
    >>> 'Login Name' in browser.contents
    True

    >>> browser.open('%s/edit' % self.folder.document1.absolute_url())
    >>> 'Login Name' in browser.contents
    True


Test with the member role
-------------------------
Logout, so that we can inspect our item as another user of the system

    >>> browser.open('%s/logout' % self.portal.absolute_url())
    >>> browser.open('%s/login_form' % self.portal.absolute_url())
    >>> browser.getControl(name='__ac_name').value = 'member'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl('Log in').click()

Head over to our temporary folder containing our one_state_workflow items

    >>> browser.open('%s' % self.folder.absolute_url())

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
    LookupError: label 'Edit'
    >>> browser.open('%s' % self.folder.document1.absolute_url())
    >>> browser.getControl('Edit')
    Traceback (most recent call last):
    ...
    LookupError: label 'Edit'

Or have the "Modify portal content" permission in any scenario

    >>> # browser.open('%s/edit' % self.folder.absolute_url())
