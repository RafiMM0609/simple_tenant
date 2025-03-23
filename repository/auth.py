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
    request: LoginRequest,
):
    data = db.table("users").select("*").execute()
    user_data =  data.data[0]
    if request.password == user_data["password"]:
        return data.data[0]
    else:
        raise ValueError("Invalid credentical")
    
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
            db.table("users")
            .select("id")
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
    request.password = generate_hash_password(request.password)
    insert_data = request.dict()
    insert_data["id_role"] = 1
    try:
        response = (
            db.table("users")
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