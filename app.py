from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from pydantic import BaseModel,EmailStr, field_validator
from fastapi.middleware.cors import CORSMiddleware
import datetime
import jwt
import pandas as pd
from io import StringIO
import re
import os
import psycopg2
from bcrypt import hashpw,checkpw, gensalt
from sentiment import predict_sentiment
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv(raise_error_if_not_found=True))

DATABASE_CONFIG = {
    'dbname': os.getenv("pg_db_name"),
    'user': os.getenv("pg_user"),
    'password': os.getenv("pg_password"),
    'host': os.getenv("pg_host"), 
    'port': os.getenv("pg_port")        
}

app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin (can be restricted)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secret key for JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"  # Hashing algorithm for JWT



class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", value):
            raise ValueError("Password must contain at least one letter.")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number.")
        return value


def create_jwt_token(email: str):
    """
    Create a JWT token with an expiration time.
    """
    payload = {
        "sub": email,  # Subject (user's email)
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),  # Token expiry
        "iat": datetime.datetime.now(datetime.timezone.utc),  # Issued at time
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(token: str):
    """
    Verify and decode the JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]  # Return the email (or user identifier)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_user(email:str,password:str)->bool:
    try:
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        conn = psycopg2.connect(**DATABASE_CONFIG)
        print("Connection successful!")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hanabi_user (email,password)
            VALUES (%s, %s)
        """, (
            email,
            hashed_password.decode("utf-8")
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as _:
        print(_)
        return False

def validate_user(email: str, password: str) -> bool:
    try:
        # Fetch the stored hashed password from the database
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        query = "SELECT password FROM hanabi_user WHERE email=%s;"
        cursor.execute(query, (email,))
        row = cursor.fetchone()  # Fetch one row
        cursor.close()
        conn.close()
        # print(row)
        if row:
            stored_hashed_password = row[0]  # The hashed password from the DB
            # Compare the entered password with the stored hashed password
            if checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                return True  # Password is correct
            else:
                return False  # Password is incorrect
        else:
            return False  # User not found
    except Exception as _:
        print(_)
        return False

@app.post("/login/")
def login(data: LoginRequest):
    if validate_user(data.email,data.password):
        # Generate a JWT token
        token = create_jwt_token(data.email)
        return {"token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/signup/")
def signup(data: LoginRequest):
    if create_user(data.email,data.password):
        return {"response":"successful"}
    else:
        raise HTTPException(status_code=401, detail="error")


@app.post("/upload-csv/")
async def upload_csv(
    file: UploadFile = File(...),
    authorization: str = Header(None),  # Get the Authorization header
):
    # Verify the token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token missing or invalid")
    token = authorization.split(" ")[1]  # Extract the token
    email = verify_jwt_token(token)  # Verify token and get the email

    # Process the file
    content = await file.read()
    df = pd.read_csv(StringIO(content.decode("utf-8")))
    texts = df["text"].tolist()
    sentiments = predict_sentiment(texts)
    df["sentiment"] = sentiments
    sentiment_counts = df["sentiment"].value_counts().to_dict()
    sentiment_records = df.to_dict(orient="index")

    # Return results
    return {
        "user": email,  # Include user info (from token)
        "sentiment_counts": sentiment_counts,
        "sentiments": list(sentiment_records.values()),
    }
