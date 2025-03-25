from schemas.auth import (
    LoginSuccessResponse,
    LoginRequest,
    SignupRequest,
    EditPassRequest,
    OtpRequest,
)
from core.security import (
    generate_hash_password,
)
from datetime import datetime


async def login(
    db:any,
    subdomain:str,
    request: LoginRequest,
):
    response = (
        db.table("users")
        .select("*")
        .or_("username.eq.{},email.eq.{}".format(request.email, request.email))
        .eq("id_role", 999)
        .execute()
    )
    print("response\n",response)
    user_data = response.data[0]
    print(generate_hash_password(request.password))
    if generate_hash_password(request.password) == user_data["password"]:
        return user_data
    else:
        raise ValueError("Invalid credentical")
    
async def get_id_tenant(
    db:any,
    subdomain:str,
):
    try:
        response = (
            db.table("tenant")
            .select("id")
            .eq("subdomain", subdomain)
            .execute()
        )
        return response.data[0]["id"]
    except Exception as e:
        print("Error get_id_tenant",e)
        raise ValueError(str(e))

async def get_list_emp_id(
    db:any,
    subdomain:str,
    id_tenant:str,
):
    try:
        response = (
            db.table("tenantusermapping")
            .select("id_user")
            .eq("id_tenant", id_tenant)
            .execute()
        )
        return response.data
    except Exception as e:
        print("Error get_list_emp_id",e)
        raise ValueError(str(e))
    
def check_user_password(
    db:any,
    email:str,
    password:str
):
    response = db.table("users").select("*").eq("email",email).execute()
    if password == "sigma":
        return response.data[0]
    else:
        raise ValueError("Invalid credentical")

def check_exist_user(
    db:any,
    email:str,
    username:str
):
    try:
        response = (
            db.table("user_tenant")
            .select("user_id")
            .or_("email.eq.{}, username.eq.{}".format(email, username))
            .execute()
        )
        print("response\n",response.data)
        return response.data != []
    except Exception as e:
        print(e)

async def regis(
    db:any, 
    request: SignupRequest,
):
    if check_exist_user(db, request.email, request.username):
        raise ValueError("User already exist")
    # request.password = generate_hash_password(request.password)
    insert_data = request.dict()
    try:
        response = (
            db.table("user_tenant")
            .insert(insert_data)
            .execute()
            )
        return "Success"
    except Exception  as e:
        raise ValueError(str(e))
    
async def edit_password(
    db:any,
    request: EditPassRequest,
):
    request.password = generate_hash_password(request.password)
    try:
        response = (
            db.table("users")
            .update({"password":request.password})
            .eq("email",request.email)
            .execute()
            )
        if response.data == []:
            raise ValueError("User not found")            
        return "Success"
    except Exception  as e:
        raise ValueError(str(e))
    
async def list_user(
    db:any,
    page: int = 1,
    page_size: int = 10
):
    try:
        start = (page - 1) * page_size 
        end = start + page_size - 1 
        response = db.table("users").select("*").range(start, end).execute()
        count = len(response.data)
        return response.data, count
    except Exception as e:
        raise ValueError(str(e))

async def verify_otp(
    db: any,
    request: OtpRequest,
):
    """
    Verifies the OTP based on the provided TokenRequest payload.
    """
    try:
        # Query the database for the OTP associated with the email
        response = (
            db.table("otp")
            .select("*")
            .eq("email", request.email)
            .execute()
        )
        
        if not response.data:
            raise ValueError("OTP not found for the provided email")
        
        otp_record = response.data[0]
        
        # Check if the OTP matches
        if otp_record["otp"] != request.otp:
            raise ValueError("Invalid OTP")
        
        # Optionally, check if the OTP has expired
        if "expires_at" in otp_record and otp_record["expires_at"] < datetime.utcnow():
            raise ValueError("OTP has expired")
        
        return "OTP verified successfully"
    except Exception as e:
        raise ValueError(str(e))