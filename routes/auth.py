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
from schemas.auth import (
    LoginSuccessResponse,
    LoginRequest,
    MeSuccessResponse,
    RegisSuccessResponse,
    SignupRequest,
    CadSuccessResponse,
    EditPassRequest,
    ListUserRequest
)
import repository.auth  as authRepo
router = APIRouter(tags=["Auth"])


@router.post(
    "/login",
    responses={
        "200": {"model": LoginSuccessResponse},
        "400": {"model": BadRequestResponse},
        "500": {"model": InternalServerErrorResponse},
    },
)
async def login(
    request: LoginRequest, 
    db: Client = Depends(get_supabase)
):
    try:
        data = await authRepo.login(db=db,request=request)
        token = await generate_jwt_token_from_user(user=data)
        return common_response(
            Ok(
                data={
                    "email": request.email,
                    "is_active": True,
                    "role": {
                        "nama": "admin",
                        "id": 1
                    },
                    "token": token
                }
            )
        )
    except Exception as e:
        return common_response(BadRequest(message=str(e)))
    

@router.post("/token")
async def generate_token(
    db: Client = Depends(get_supabase), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        is_valid = authRepo.check_user_password(
            db, form_data.username, form_data.password
        )
        if not is_valid:
            return common_response(BadRequest(message="Invalid Credentials"))
        user = is_valid
        token = await generate_jwt_token_from_user(user=user)
        return {"access_token": token, "token_type": "Bearer"}
    except Exception as e:
        return common_response(BadRequest(error=str(e)))
    
@router.get(
    "/me",
    responses={
        "200": {"model": MeSuccessResponse},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "500": {"model": InternalServerErrorResponse},
    },
)
async def me(
        db: Client = Depends(get_supabase),
        token: str = Depends(oauth2_scheme)
        ):
    try:        
        request_user = get_user_from_jwt_token(model='user',db=db, jwt_token=token)
        if request_user == None:
            return common_response(Unauthorized(message="Invalid/Expired token"))
        # db = request.state.db
        # refresh_token = await generate_jwt_token_from_user(user=user)
        return common_response(
            Ok(
                data={
                    "id": str(request_user['id']),
                    "email": request_user['email'],
                    "username": request_user['username'],
                }
            )
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        return common_response(BadRequest(message=str(e)))
    
@router.post(
    "/regis",
    responses={
        "200": {"model": RegisSuccessResponse},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "500": {"model": InternalServerErrorResponse},
    },
)
async def regis(
    request: SignupRequest, 
    db: Client = Depends(get_supabase)
):
    try:
        # errors = UserRegisValidator().validate(request.dict())
        # errors_list = [key for key in errors.keys()]
        # if errors != {}:
        #     # return common_response(BadRequest(custom_response=errors))
        #     return common_response(BadRequest(message=f"Data that you sent is not valid! please check this field {errors_list}"))

        data = await authRepo.regis(db=db,request=request)
        
        return common_response(
            Ok(
                data={
                    "data": "Success"
                }
            )
        )
    except Exception as e:
        return common_response(BadRequest(message=str(e))
)
    
@router.post(
    "/edit-password",
    responses={
        "200": {"model": CadSuccessResponse},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "500": {"model": InternalServerErrorResponse},
    },
)
async def edit_password(
    request: EditPassRequest, 
    db: Client = Depends(get_supabase)
):
    try:
        data = await authRepo.edit_password(db=db,request=request)
        return common_response(
            Ok(
                data={
                    "data": "Success"
                }
            )
        )
    except Exception as e:
        return common_response(BadRequest(message=str(e))
)
    
@router.get(
    "/list-user",
    responses={
        "200": {"model": MeSuccessResponse},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "500": {"model": InternalServerErrorResponse},
    },
)
async def list_user(
    db: Client = Depends(get_supabase),
    page: int = 1,
    page_size: int = 10
):
    try:
        data, count = await authRepo.list_user(db=db, page=page, page_size=page_size)
        print("disini")
        return common_response(
            Ok(
                data={
                    "total": count,
                    "page": page,
                    "page_size": page_size,
                    "results" : 
                    [
                        {
                            "email": x["email"],
                            "username": x["username"],
                            "phone_number": x["phone_number"],
                        } for x in data
                    ]
                }
            )
        )
    except Exception as e:
        return common_response(BadRequest(message=str(e))
)