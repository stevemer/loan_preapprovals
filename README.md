# loan_preapprovals
A small API that pre-approves consumers for an imagined loan.

Notes:

## This server includes none of the following:
- logging
- TTLing, or similar, of database
- rate limiting
- login (possibly fine, though, for a marketing funnel)
- metrics/monitoring
- email configuration

## Config
The financial variables in this API are set via `config/config.py`. The file is protected by goldens via hexdigest. There is some improvement to be done to the test cleanliness - instead of referencing the constants from the test suite, as I did in some places, it'd be preferable to mock the constants to a consistent test value, then hardcode the numbers used in the tests, to make test behavior more legible.

## Live Instance
This server is hosted on a develoment-tier single-dyno instance at `loan-preapprover-prod.herokuapp.com`.

Suggested starting query: `http post loan-preapprover-prod.herokuapp.com/users name=jake` using httpie.
