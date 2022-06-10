###################
Titans Email Client
###################

This package handles sending emails to all of our subscribers, all from the
command line.

**************
Authenticating
**************

For first-time use, you must authenticate with Office365 by following these
steps:

In the Azure portal:

#. Go to :code:`Azure Active Directory` -> :code:`App Registrations`

#. Create a new app registration. Set the redirect URI to
   :code:`http://localhost`.

#. Go to :code:`Certificates & secrets`, then create a new client secret. Copy
   the :code:`Value`, as you'll only be able to see this once.

#. Go to :code:`API Permissions`, and from Microsoft Graph the Delegated
   Permission of Mail.Send.

#. Create a :code:`~/secrets/titans-email-creds` file that looks like:

   .. code-block:: bash
      
      #!/bin/bash

      TENANT=<directory (tenant) id>
      CLIENT_ID=<application (client) id>
      CLIENT_SECRET=<certifiacte & secrets value>

In this repo:

#. Make sure you have a :code:`SECRETS_DIR` environmental variable set, e.g.
   :code:`~/secrets`.

#. Run :code:`auth/get-code.sh`. Follow the website it points you to, and
   authenticate with your office account. It'll redirect you to an error page.
   On that page, look at the url, and copy the :code:`code` parameter from the
   URL (i.e. the portion that reads :code:`&code=...&`). Paste that code into a
   :code:`$SECRETS_DIR/titans-email-code` file in this repo.

#. Run `auth/get-token.sh`. This will create a
   :code:`$SECRETS_DIR/titans-email-token` file, containing your
   authentication token.

**************
Sending Emails
**************

We recommend pip-installing this package, and then sending emails using the
command-line interface:

.. code-block:: bash

   python -m titansemail yamlconfig

where :code:`yamlconfig` is a configuration yaml file that is unpacked to
initialize :code:`titansemail.sender.SendEmails`. An example configuration yaml
file would look like:

.. code-block:: yaml

   subject: We're Back!
   body: 2022-07/body.html
   attachments: [
     2022-07/box.png,
     2022-07/divider.png,
     2022-07/final_judgment.png,
     2022-07/logo.png,
   ]

where :code:`2022-07/body.html` is the name of an html file you want to send,
and the attachments are names of attachments you want to attach.

Please note that any attachments can be referenced in :code:`body` via their
cid:

.. code-block:: html

   <img src="cid:logo">

and the string :code:`#|EMAIL|#` will be replaced with the receipient's email
address.

************
Dev: Testing
************

Send a test email:

.. code-block:: bash

   python tests/send_test.py

This can also be invoked with :code:`pytest`
