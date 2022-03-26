class Error:
    UnknownMethod = 'Unknown method'
    InvalidRequest = 'Invalid request, check query parameters'
    NoResult = 'No result'
    UserNotFound = 'User is not found'

    error_code = {
        1: UnknownMethod,
        2: InvalidRequest,
        3: NoResult,
        4: UserNotFound
    }

