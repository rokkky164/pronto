"""
Account constants
"""

"""
URL start
"""
APP_NAME = "accounts"
PASSWORD_PREFIX = r'password'
PASSWORD_BASENAME = 'password'
PASSWORD_CHANGE_NAME = 'change'
PASSWORD_RESET_NAME = 'reset'
PASSWORD_VERIFY = 'verify'
USER_PREFIX = r'user'
USER_BASENAME = 'user'

USER_EXAM_TYPE_URL_NAME = 'user-exam-type-list'

COMPANY_INFORMATION_URL_NAME = 'company-information'
ACCOUNT_MANAGER_DETAILS_URL_NAME = 'account-manager-details'
LOGIN_URL_NAME = 'login'
TOKEN_REFRESH_URL_NAME = 'token_refresh'
REGISTER_URL_NAME = 'register'
ACCOUNT_VERIFY_URL_NAME = 'account-verify'
RESEND_VERIFICATION_CODE_URL_NAME = 'resend-verification-code'
SEND_MAIL_FOR_REGISTRATION = 'send-mail-for-registration'

USER_BY_EMAIL_URL = 'user-by-email'
USER_BY_EMAIL_URL_NAME = 'user-by-email'

DELETE_ACCOUNT_REQUEST_URL = 'delete-account-request'
DELETE_ACCOUNT_REQUEST_URL_NAME = 'delete-account-request'

SEND_DELETE_REQUEST_EMAIl_URL = 'send-delete-email'
SEND_DELETE_REQUEST_EMAIl_URL_NAME = 'send-delete-email'

"""
URL end
"""

"""
Model constants start.
"""

OS_MAX_LENGTH = 50
VERSION_MAX_LENGTH = 20
IP_ADDRESS_MAX_LENGTH = 20
BROWSER_MAX_LENGTH = 50
DEVICE_TYPE_MAX_LENGTH = 6
DEVICE_MAX_LENGTH = 50

# Validation messages
USERNAME_VALIDATION_MESSAGE = 'Enter a valid username. This value may contain only English letters, '\
                               'numbers, and ./-/_ non-repeating special characters.'
FIRST_NAME_VALIDATION_MESSAGE = 'First Name can only contain letters & non-repeating special characters dot, ' \
                                'quote and hyphen'
FIRST_NAME_MINIMUM_LENGTH_MESSAGE = 'Minimum 2 characters are required'
FIRST_NAME_MAXIMUM_LENGTH_MESSAGE = 'Maximum 40 characters are allowed'
LAST_NAME_VALIDATION_MESSAGE = 'Last Name can only contain letters, spaces & non-repeating special characters dot, ' \
                               'quote and hyphen'
LAST_NAME_MAXIMUM_LENGTH_MESSAGE = 'Maximum 50 characters are allowed'
EMAIL_ALREADY_EXIST = 'This email is already registered.'

"""
Model constants end.
"""

"""
Email start
"""
#   initiate account verification
ACCOUNT_ACTIVATION_MAIL_SUBJECT = "Please activate your account."
ACCOUNT_ACTIVATION_MAIL_HEADER = "An account was created/updated with following details on prep.study:"
ACCOUNT_ACTIVATION_MAIL_MESSAGE = "If you have not carried out this action, you may ignore and delete " \
                                           "this e-mail. Else, to verify this e-mail address and associate it with " \
                                           "above mentioned user account, use the below OTP"
ACCOUNT_ACTIVATION_MAIL_TAG = "activation"

#   Password reset
SEND_PASSWORD_RESET_MAIL_HEADER = "There was a request to change your password!"
SEND_PASSWORD_RESET_MAIL_SUBJECT = "Password Reset"
SEND_PASSWORD_RESET_MAIL_MESSAGE = "If you have not carried out this action, you may ignore and delete this e-mail. " \
                              "Else, to reset the password, use the below OTP."
SEND_PASSWORD_RESET_MAIL_TAG = "password-reset"

# Resend verification code
RESEND_VERIFICATION_MAIL_SUBJECT = "Please activate your account"
RESEND_VERIFICATION_MAIL_MESSAGE = "If you have not carried out this action, you may ignore and delete this e-mail. " \
                                   "Else, to verify this e-mail address and associate it with above " \
                                   "mentioned user account, use the below OTP."
RESEND_VERIFICATION_MAIL_TAG = "activation"
# Send email verification
SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_SUBJECT = "Email Change Request"
SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_HEADER = "There was a request to change your email address!"
SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_MESSAGE = "If you have not carried out this action, you may ignore and delete " \
                                               "this e-mail. Else, to change the email, " \
                                               "use the below verification code."
SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_TAG = "email-change"
# Send Registration Mail to Potential User
SEND_EMAIL_TO_NEW_USER_HEADER = "Please use this link to login to corporate"
SEND_EMAIL_TO_NEW_USER_HEADER_CORPORATE = "We are excited to move forward with your application and as the first step in" \
                                          "our hiring process, we would like to invite you to complete an online" \
                                           "assessment designed to assess your skills & qualifications for the position."
SEND_EMAIL_TO_NEW_USER_SUBJECT = "Welcome to Prep.Study Corporate"
SEND_EMAIL_TO_NEW_USER_MESSAGE = "We’d like to invite you to onboard our portal.To login please use the below credentials.\n"\
                                       "Username: {username}\n"\
                                       "Password: {password}"
SEND_EMAIL_TO_NEW_USER_MESSAGE_SUPPORT = "We’d like to invite you to onboard our portal.To login please use the below credentials.\n"\
                                       "Username: {username}\n"\
                                       "Password: {password}\n"\
                                       "If you experience any issues while login, reach out to us at {support_email}."
SEND_EMAIL_TO_NEW_USER_HEADER_V2 = "Please use this link to login to Prep.Study V2"
SEND_EMAIL_TO_NEW_USER_TAG = "new-user-corporate"
SEND_EMAIL_TO_NEW_USER_SUBJECT_V2 = "Welcome to Prep.Study V2"
SEND_EMAIL_TO_NEW_USER_TAG_V2 = "new-user-v2"
SEND_EMAIL_TO_NEW_USER_SUBJECT_CROPORATE  = "Welcome to {org_name}"

DELETE_USER_ACCOUNT_REQUEST_SUCCESS = ("Request successfully generated. "
                                       "The account will be deleted "
                                       "if there is no login activity within the next 7 days.")
DELETE_USER_ACCOUNT_REQUEST_EXPIRED = 'The account delete request is expired.'
SEND_DELETE_REQUEST_HEADER = "Confirmation required for Account Deletion Request"
SEND_DELETE_REQUEST_MAIL_TAG = "delete-reset"
SEND_DELETE_REQUEST_MAIL_SUBJECT = "Confirmation for Account Deletion Request"


"""
Email end
"""

"""
Response message start
"""
#   Permission
YOU_ARE_NOT_ALLOWED_TO_ACCESS_SCHOOL = 'You are not allowed to access this school.'
YOU_ARE_NOT_ALLOWED_TO_CHANGE_EMAIL = 'You are not allowed to change email address'
# Common
INVALID_CREDENTIALS = 'Invalid credentials.'
INVALID_DATA = 'Invalid data.'
#   Register
COMPANY_INFORMATION_CREATION_SUCCESS = 'Company Information created successfully.'
COMPANY_INFORMATION_CREATION_FAILED = "Company Information creation failed."
COMPANY_INFORMATION_FETCH_SUCCESS = 'Company Information fetched successfully.'
COMPANY_INFORMATION_NOT_FOUND = "Company Information not found."

ACCOUNT_MANAGER_CREATION_SUCCESS = 'Account Manager created successfully.'
ACCOUNT_MANAGER_CREATION_FAILED = "Account Manager creation failed."
ACCOUNT_MANAGER_FETCH_SUCCESS = 'Account Manager fetched successfully.'
ACCOUNT_MANAGER_NOT_FOUND = "Account Manager not found."

EITHER_MOBILE_OR_EMAIL_REQUIRED = "Either Mobile number or Email is required."
PROVIDED_ROLE_DOES_NOT_EXIST = "Provided role doesn't exist."
GRADE_FIELD_REQUIRED_STUDENT = "Grade/Degree field is required for student user."
EMAIL_IS_REGISTERED = 'This email is already registered.'
USERNAME_IS_REGISTERED = 'This username is already registered.'
NUMBER_IS_REGISTERED = 'This number is already registered.'
#   Account verify
ACTIVATED_ACCOUNT_SUCCESS = 'Activated the account successfully.'
INVALID_VERIFICATION_CODE = 'Invalid verification code.'
VERIFICATION_CODE_EXPIRED = 'Verification code expired.'
VERIFICATION_CODE_ALREADY_USED = 'Verification code already used.'
VERIFICATION_CODE_REQUIRED = 'Verification code required.'
#   Password
PASSWORD_CHANGE_SUCCESS = 'Password changed successfully.'
PASSWORD_RESET_REQUEST_SENT_SUCCESS = 'Password reset request sent successfully.'
PASSWORD_CHANGE_FAILED = 'Password change failed.'
PASSWORD_RESET_REQUEST_FAILED = 'Password reset request failed.'
INVALID_CURRENT_PASSWORD = 'Invalid current password.'
BOTH_PASSWORD_MUST_SAME = "Both passwords must be same."
NEW_PASSWORD_SAME_AS_CURRENT_PASSWORD = 'New password cannot be the same as your current password.'
USER_OBJECT_NOT_PROVIDED = 'User object not provided.'
USER_NOT_PROVIDED_IN_SERIALIZER_CONTEXT = 'User not provided in serializer context.'
#   User
USER_LIST_FETCH_SUCCESS = 'User list fetched successfully.'
USER_DETAIL_FETCH_SUCCESS = 'User detail fetched successfully.'
USER_UPDATE_SUCCESS = 'User updated successfully.'
USER_NOT_FOUND = 'User not found.'
CITY_DOES_NOT_EXIST = 'City does not exist.'
STATE_DOES_NOT_EXIST = 'State does not exist.'
COUNTRY_DOES_NOT_EXIST = 'Country does not exist.'
INVALID_GRADE = 'Invalid grade.'
INVALID_SECTION = 'Invalid section.'
INVALID_MOBILE_NUMBER = 'Invalid mobile number.'
INVALID_SCHOOL_PROVIDED = 'Invalid school provided.'
INVALID_AUTH_CODE = "Invalid auth code."
USER_EXAM_TYPE_FETCH_SUCCESS = "Exam types fetch successfully."
USER_BY_EMAIL_FETCH_SUCCESS = 'User by email fetched successfully.'

AVATAR_LIST_FETCH_SUCCESS = "User avatar list fetched successfully"

#   Email
EMAIL_CHANGE_REQUEST_CREATE_SUCCESS = 'Email change request created successfully.'
EMAIL_CHANGE_SUCCESS = 'Email changed successfully.'
UNABLE_TO_CREATE_EMAIL_CHANGE_REQUEST = 'Unable to create email change request.'
EXPECTED_VERIFICATION_CODE_AS_QUERY_PARAMETER = 'Expected verification_code as query parameter.'
INVALID_OR_EXPIRED_VERIFICATION_CODE = 'Invalid or expired verification code.'
INCORRECT_EMAIL = 'Incorrect email.'
SEND_DELETE_REQUEST_EMAIL_SUCCESS = 'Send delete request email successfully.'
#   Login
LOGIN_SUCCESS = 'Login successful.'
LOGIN_FAILED = 'Login failed.'
EITHER_USERNAME_AND_PASSWORD_OR_AUTH_CODE_REQUIRED = 'Either username and password OR auth_code is required.'
ACCOUNT_NOT_ACTIVATED_YET = 'Account not activated yet.'
INVALID_USERNAME = 'Invalid Username.'
INACTIVATED_ACCOUNT = 'Please activate your account.'
#   Custom token
ACCESS_TOKEN_RENEWED_SUCCESS = 'Access token renewed successfully.'
FAILED_TO_RENEW_ACCESS_TOKEN = 'Failed to renew access token.'
# Send verification code
AUTHENTICATION_CODE_SEND_SUCCESS = "Authentication code send successfully."
USER_NOT_FOUND_WITH_GIVEN_MAIL_ID = "User not found with given mail id."

PIN_CODE_LIST_FETCH_SUCCESS = 'Pin code list fetched successfully.'

CITY_STATE_SHOULD_BE_PROVIDED_WHEN_UPDATING_THE_COUNTRY = 'City and State should be provided when updating the Country.'
CITY_SHOULD_BE_PROVIDED_WHEN_UPDATING_THE_STATE = 'City should be provided when updating the State.'
COUNTRY_STATE_CITY_HIERARCHY_DO_NOT_MATCH = 'Country, State and City hierarchy do not match.'
# Send Mail for Registration
SEND_MAIL_FOR_REGISTRATION_SUCCESS = 'Mail was sent successfully to user.'
UNABLE_TO_SEND_MAIL_FOR_REGISTRATION = 'Unable to send mail to the user.'
USER_CREDS_SENT_SUCCESS = 'User credentials have been sent successfully.'

# Temp files folder
# TEMP_FOLDER_FOR_STUDENTS = "media/bulk_upload/STUDENT/temp_file"
# TEMP_FILE_FOR_STUDENTS = f"{TEMP_FOLDER_FOR_STUDENTS}/students.xlsx"

# TEMP_FOLDER_FOR_TEACHERS = "media/bulk_upload/STUDENT/temp_file"
# TEMP_FILE_FOR_TEACHERS = f"{TEMP_FOLDER_FOR_TEACHERS}/students.xlsx"
"""
Response message end
"""
