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

#. Create a :code:`~/secrets/titans-emailclient` file that looks like:

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
   :code:`$SECRETS_DIR/titans-email-token-local` file, containing your
   authentication token.

#. Test by running :code:`test/send.sh`, updating the recipient email to your
   target test email.
