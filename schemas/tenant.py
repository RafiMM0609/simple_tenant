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

class EditTenantRequest(BaseModel):
    tenant_name:str
    email:str
    phone:str
    subdomain:str

class RegisTenantRequest(BaseModel):
    tenant_name:str
    contact_email:str
    phone:str
    subdomain:Optional[str]=None

class DataTenant(BaseModel):
    tenant_name:str
    contact_email:str
    phone:str
    created_at:Optional[str]="08/11/2025"
    updated_at:Optional[str]="29/12/2025"
    subdomain:Optional[str]=None
    tenant_code:Optional[str]=None

class ListDataTenantResponse(BaseModel):
    meta: MetaResponse
    data: DataTenant
    status: str
    code: int
    message: str

class DataUserMapping(BaseModel):
    username:str
    email:str
    phone:str
    tenant_name:str
    created_at:str="08/11/2025"
    updated_at:str="29/12/2025"

class DataUserMappingResponse(BaseModel):
    meta: MetaResponse
    data: DataUserMapping
    status: str
    code: int
    message: str


class DataUserDir(BaseModel):
    userid:int
    email:str
    phone:str
    username:str
    id_tenant:Optional[str]=None
    tenant_name:str
    tenant_code:str
    created_at:str="08/11/2025"
    updated_at:Optional[str]=None


class DataUserDirResponse(BaseModel):
    meta: MetaResponse
    data: DataUserDir
    status: str
    code: int
    message: str