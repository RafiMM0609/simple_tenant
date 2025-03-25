from typing import List, Optional
from pydantic import BaseModel

class MetaResponse(BaseModel):
    count:int
    page_count:int
    page_size:int
    page:int

class CreateSuccessResponse(BaseModel):
    meta: MetaResponse
    data: None
    status: str
    code: int
    message: str

class Organization(BaseModel):
    id: int
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginSuccess(BaseModel):
    id: str
    email: str
    is_active: bool
    role: Organization
    token: str

class LoginSuccessResponse(BaseModel):
    meta: MetaResponse
    data: LoginSuccess
    status: str
    code: int
    message: str

class MeSuccess(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    refreshed_token: str

    class RoleDetail(BaseModel):
        id: int
        nama: str

        class GroupDetail(BaseModel):
            id: int
            nama: str

        group: Optional[GroupDetail]

    role: RoleDetail

    NIK: Optional[str]
    signature_path: Optional[str]

class SignupRequest(BaseModel):
    email:str
    phone:str
    password:str
    username:str
    # picture:Optional[str]=None

class MeSuccessResponse(BaseModel):
    meta: MetaResponse
    data: MeSuccess
    status: str
    code: int
    message: str
    
class EditPassRequest(BaseModel):
    email:str
    password: str
    confim_password: str

class RegisSuccessResponse(BaseModel):
    message:str
class CadSuccessResponse(BaseModel):
    message:str

class ListUserRequest(BaseModel):
    page: int = 1,
    page_size: int = 10
class MeRequest(BaseModel):
    token: str

class OtpRequest(BaseModel):
    otp: str
