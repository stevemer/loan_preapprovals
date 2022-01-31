# Constants for loan calculation.
# This setup makes the loan engine flexible to reconfigure if loan rates
# change in the future, while protecting the configuration against accidental
# changes. These constants could still be moved into environment variables
# on the deployed instances, while keeping this source of truth checked into
# version control, ensuring appropriate review and test coverage.

# User will be assigned the highest band that they are eligible for.
# These are in descending order by minimum_score_required.
# This ordering is enforced by test coverage.
CREDIT_BANDS = [{
    "minimum_score_required": 780,
    "apr": 0.02,
}, {
    "minimum_score_required": 720,
    "apr": 0.05,
}, {
    "minimum_score_required": 660,
    "apr": 0.09,
}]

# If more then X bankruptcies are found, the application will be declined.
MAXIMUM_BANKRUPTCIES = 0

# If more then X delinquencies are found, the application will be declined.
MAXIMUM_DELINQUENCIES = 1

# If total monthly debt payments (including new loan offer monthly payment)
# exceed X% of monthly income, the application will be declined.
MAXIMUM_DEBT_TO_INCOME_RATIO = 0.60

# If trying to borrow more money than X% of the vehicle value,
# the application will be declined.
MAXIMUM_LOAN_TO_VALUE_RATIO = 1

# The number of months in the loan term currently offered.
LOAN_LENGTH_IN_MONTHS = 72
