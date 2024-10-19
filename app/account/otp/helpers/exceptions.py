class TotpException(BaseException):
    """"""


class TotpVerificationFailedException(TotpException):
    """"""


class TotpCreationFailedException(TotpException):
    """"""


class TotpRemovalFailedException(TotpException):
    """"""


class TotpAlreadySetException(TotpException):
    """"""
