from typing import List, Optional
from fastapi import APIRouter, Depends, Request, BackgroundTasks, UploadFile, File, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from supabase import Client
from core.responses import (
    common_response,
    Ok,
    CudResponse,
    BadRequest,
    Unauthorized,
    NotFound,
    InternalServerError,
)
from validator.auth import UserRegisValidator
from models import get_supabase
from core.security import get_user_from_jwt_token, generate_jwt_token_from_user
# from models import get_db_sync
from core.security import (
    get_user_from_jwt_token,
    oauth2_scheme,
)
from schemas.common import (
    BadRequestResponse,
    UnauthorizedResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)
from schemas.tenant import (
    CreateSuccessResponse,
    RegisTenantRequest,
    EditTenantRequest,
    ListDataTenantResponse,
    DataUserDirResponse,
)
import repository.tenant  as tenantRepo
router = APIRouter(tags=["Tenant"])


@router.post(
    "",
    responses={
        "201": {"model": CreateSuccessResponse},
        "400": {"model": BadRequestResponse},
        "500": {"model": InternalServerErrorResponse},
    },
)
async def add_router(
    request: RegisTenantRequest, 
    db: Client = Depends(get_supabase),
    token: str = Depends(oauth2_scheme),
):
    try:
        user = get_user_from_jwt_token(db, "user_tenant",token)
        if not user:
            return common_response(Unauthorized())
        data = await tenantRepo.add_tenant(db=db,payload=request)
        return common_response(
            Ok(
                message="Sucess add data"
            )
        )
    except Exception as e:
        return common_response(BadRequest(message=str(e)))
    
@router.get(
    "/list",
    responses={
        "200": {"model": ListDataTenantResponse},
        "400": {"model": BadRequestResponse},
        "500": {"model": InternalServerErrorResponse},
    },
)
async def get_list_router(
    db: Client = Depends(get_supabase),
    token: str = Depends(oauth2_scheme),
):
    try:
        user = get_user_from_jwt_token(db, "user_tenant",token)
        if not user:
            return common_response(Unauthorized())
        data = await tenantRepo.get_tenants(db=db)
        return common_response(
            Ok(
                message="Sucess add data",
                data=data,
            )
        )
    except Exception as e:
        return common_response(BadRequest(message=str(e)))
    
@router.get(
    "/list-user",
    responses={
        "200": {"model": DataUserDirResponse},
        "400": {"model": BadRequestResponse},
        "500": {"model": InternalServerErrorResponse},
    },
)
async def get_list_router(
    db: Client = Depends(get_supabase),
    token: str = Depends(oauth2_scheme),
    tenant_code: Optional[str] = None,
    src: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
):
    try:
        user = get_user_from_jwt_token(db, "user_tenant",token)
        if not user:
            return common_response(Unauthorized())
        data, total_count, total_pages = await tenantRepo.get_list_user_dir(
            db=db,
            tenant_code=tenant_code,
            src=src,
            )
        return common_response(
            Ok(
                message="Sucess add data",
                data=data,
                meta={
                    "count": total_count,
                    "page_count": total_pages,
                    "page_size": page_size,
                    "page": page,
                }
            )
        )
    except Exception as e:
        return common_response(BadRequest(message=str(e)))
    
@router.post(
    "/deploy/{id_tenant}",
    responses={
        "201": {"model": CreateSuccessResponse},
        "400": {"model": BadRequestResponse},
        "500": {"model": InternalServerErrorResponse},
    },
)
async def add_service_router(
    tenant_code:str,
    token: str = Depends(oauth2_scheme),
    db: Client = Depends(get_supabase)
):
    try:
        user = get_user_from_jwt_token(db, "user_tenant",token)
        if not user:
            return common_response(Unauthorized())
        data = await tenantRepo.generate_service_yaml(db=db,tenant_code=tenant_code)
        return common_response(
            Ok(
                message="Sucess add data"
            )
        )
    except Exception as e:
        return common_response(BadRequest(message=str(e)))
