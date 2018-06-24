======================================
Functional Testing of the Sharing Page
======================================

The test setup has already ensured that we have a number of users available.
Let's also create some

    >>> from plone.testing.z2 import Browser

    >>> app = layer['app']
    >>> portal = layer['portal']
    >>> request = layer['request']

    >>> portal_url = portal.absolute_url()
    >>> folder_url = '%s/folder1' % portal_url

    >>> browser = Browser(app)
    >>> browser.handleErrors = False


Anonymous users
---------------

When we log out, we cannot see the "Sharing" tab at all.

    >>> browser.open('%s/logout' % portal_url)
    >>> browser.open(folder_url)

We're not forced to log in and we can view the item. Thus, we have view
permission.

    >>> 'Please log in' not in browser.contents
    True

We shouldn't see the Sharing tab

    >>> browser.getLink('Sharing')
    Traceback (most recent call last):
    ...
    zope.testbrowser.browser.LinkNotFoundError

Manager
-------

A Manager should be able to delegate all the accessible roles. Let's also
take this opportunity to delegate some roles so that we can check what the
other roles can do.

    >>> browser.open('%s/logout' % portal_url)
    >>> browser.open('%s/login_form' % portal_url)
    >>> browser.getControl(name='__ac_name').value = 'manager'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl('Log in').click()

    >>> browser.open(folder_url)
    >>> browser.getLink('Sharing').click()

    >>> "Can add" in browser.contents
    True
    >>> "Can edit" in browser.contents
    True
    >>> "Can manage" in browser.contents
    False
    >>> "Can own" in browser.contents
    False
    >>> "Can subscribe" in browser.contents
    False
    >>> "Can view" in browser.contents
    True
    >>> "Can review" in browser.contents
    True

    >>> browser.getControl(name='search_term').value = "delegate_contributor"
    >>> browser.getControl(name='form.button.Search').click()
    >>> 'Changes saved' not in browser.contents
    True
    >>> browser.getControl(name='entries.role_Contributor:records').getControl(value='True',index=-1).click()
    >>> request.form['form.button.Save'] = 1
    >>> browser.getControl("Save").click()
    >>> 'Changes saved' in browser.contents
    True

    >>> browser.getControl(name='search_term').value = "delegate_editor"
    >>> browser.getControl(name='form.button.Search').click()
    >>> browser.getControl(name='entries.role_Editor:records').getControl(value='True',index=-1).click()
    >>> request.form['form.button.Save'] = 1
    >>> browser.getControl("Save").click()
    >>> 'Changes saved' in browser.contents
    True

    >>> #browser.getControl(name='search_term').value = "delegate_manager"
    >>> #browser.getControl(name='form.button.Search').click()
    >>> #browser.getControl(name='entries.role_Manager:records').getControl(value='True',index=-1).click()
    >>> #request = self.portal.REQUEST
    >>> #request.form['form.button.Save'] = 1
    >>> #browser.getControl("Save").click()
    >>> #'Changes saved' in browser.contents

    >>> browser.getControl(name='search_term').value = "delegate_reader"
    >>> browser.getControl(name='form.button.Search').click()
    >>> browser.getControl(name='entries.role_Reader:records').getControl(value='True',index=-1).click()
    >>> request.form['form.button.Save'] = 1
    >>> browser.getControl("Save").click()
    >>> 'Changes saved' in browser.contents
    True

    >>> browser.getControl(name='search_term').value = "delegate_reviewer"
    >>> browser.getControl(name='form.button.Search').click()
    >>> browser.getControl(name='entries.role_Reviewer:records').getControl(value='True',index=-1).click()
    >>> request.form['form.button.Save'] = 1
    >>> browser.getControl("Save").click()
    >>> 'Changes saved' in browser.contents
    True

Owner
-----

The owner should be able to delegate Reader, Editor and Contributor.

    >>> browser.open('%s/logout' % portal_url)
    >>> browser.open('%s/login_form' % portal_url)
    >>> browser.getControl(name='__ac_name').value = 'member'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl('Log in').click()

    >>> browser.open(folder_url)
    >>> browser.getLink('Sharing').click()

    >>> "Can add" in browser.contents
    True
    >>> "Can edit" in browser.contents
    True
    >>> "Can manage" in browser.contents
    False
    >>> "Can own" in browser.contents
    False
    >>> "Can subscribe" in browser.contents
    False
    >>> "Can view" in browser.contents
    True
    >>> "Can review" in browser.contents
    False

Delegated Reader
----------------

A delegated reader should only be able to view the page, not even get to the
Sharing tab.

    >>> browser.open('%s/logout' % portal_url)
    >>> browser.open('%s/login_form' % portal_url)
    >>> browser.getControl(name='__ac_name').value = 'delegate_reader'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl('Log in').click()

    >>> browser.open(folder_url)
    >>> browser.getLink('Sharing')
    Traceback (most recent call last):
    ...
    zope.testbrowser.browser.LinkNotFoundError

Delegated Editor
----------------

A delegated Editor can give other people "view" and "edit" rights.

    >>> browser.open('%s/logout' % portal_url)
    >>> browser.open('%s/login_form' % portal_url)
    >>> browser.getControl(name='__ac_name').value = 'delegate_editor'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl('Log in').click()

    >>> browser.open(folder_url)
    >>> browser.getLink('Sharing').click()

    >>> "Can add" in browser.contents
    False
    >>> "Can edit" in browser.contents
    True
    >>> "Can view" in browser.contents
    True
    >>> "Can review" in browser.contents
    False


Delegated Contributor
---------------------

A delegated Contributor cannot assign any further rights.

    >>> browser.open('%s/logout' % portal_url)
    >>> browser.open('%s/login_form' % portal_url)
    >>> browser.getControl(name='__ac_name').value = 'delegate_contributor'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl('Log in').click()

    >>> browser.open(folder_url)
    >>> browser.getLink('Sharing').click()
    Traceback (most recent call last):
    ...
    zope.testbrowser.browser.LinkNotFoundError

Delegated Reviewer
------------------

A delegated Reviewer can assign "view" and "review" rights.

    >>> browser.open('%s/logout' % portal_url)
    >>> browser.open('%s/login_form' % portal_url)
    >>> browser.getControl(name='__ac_name').value = 'delegate_reviewer'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl('Log in').click()

    >>> browser.open(folder_url)
    >>> browser.getLink('Sharing').click()

    >>> "Can add" in browser.contents
    False
    >>> "Can edit" in browser.contents
    False
    >>> "Can manage" in browser.contents
    False
    >>> "Can own" in browser.contents
    False
    >>> "Can subscribe" in browser.contents
    False
    >>> "Can view" in browser.contents
    True
    >>> "Can review" in browser.contents
    True

#Delegated Manager
#-----------------
#
#A delegated Manager can assign all rights.
#
#    >>> browser.open('%s/logout' % portal_url)
#    >>> browser.open('%s/login_form' % portal_url)
#    >>> browser.getControl(name='__ac_name').value = 'delegate_manager'
#    >>> browser.getControl(name='__ac_password').value = 'secret'
#    >>> browser.getControl('Log in').click()
#
#    >>> browser.open(folder_url)
#    >>> browser.getLink('Sharing').click()
#
#    >>> "Can add" in browser.contents
#    True
#    >>> "Can edit" in browser.contents
#    True
#    >>> "Can manage" in browser.contents
#    False
#    >>> "Can own" in browser.contents
#    False
#    >>> "Can subscribe" in browser.contents
#    False
#    >>> "Can view" in browser.contents
#    True
#    >>> "Can review" in browser.contents
#    True
