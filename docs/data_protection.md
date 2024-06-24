# ONS Alpha — Data Protection

This page gives an overview of potentially-sensitive data stored or processed by the ONS Alpha project.

### User accounts

What personally-identifying data is stored in a user’s account?

### Other

Describe other stored or processed data here, and steps made to ensure this is compliant with GDPR, e.g.

- visitor enquiries
- user emails, e.g. newsletter subscription requests
- customer or purchase details
- stored Wagtail FormPage submissions

## Data locations

### Logical location of data

Where is the GDPR-related data stored? Does this include any backups, or exports?

## Responding to GDPR requests

If a request is received to purge or report the stored data for a given user, what steps are needed?

- For user account data, delete the user from the Wagtail admin
- For form submissions, ask the client to handle requests as the first option. Failing that, search the submissions and delete if necessary using the Django shell.
