from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str, code: int = 0):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


class AuthenticationError(AppException):
    def __init__(self, detail: str = "认证失败"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, code=401)


class NotFoundError(AppException):
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail, code=404)


class LLMProviderError(AppException):
    def __init__(self, detail: str = "AI 服务暂时不可用"):
        super().__init__(status.HTTP_502_BAD_GATEWAY, detail, code=502)


class UploadError(AppException):
    def __init__(self, detail: str = "上传失败"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, code=400)


def error_response(code: int, message: str, request_id: str = ""):
    return {
        "code": code,
        "message": message,
        "data": None,
        "request_id": request_id,
    }


def success_response(data, request_id: str = ""):
    return {
        "code": 0,
        "message": "success",
        "data": data,
        "request_id": request_id,
    }
