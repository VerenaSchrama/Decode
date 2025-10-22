"""
Authentication service using Supabase Auth with service role for profile creation
Handles user registration, login, logout, and profile management
"""

import os
from typing import Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator

load_dotenv()

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    name: str
    age: Optional[int] = None
    date_of_birth: Optional[str] = None
    anonymous: bool = False
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Allow emails even if domain doesn't exist (for development/testing)
        try:
            from email_validator import validate_email
            validate_email(v, check_deliverability=False)  # Don't check if domain exists
            return v
        except Exception:
            # Fallback to basic email format validation
            import re
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                return v
            raise ValueError('Invalid email format')

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Allow emails even if domain doesn't exist (for development/testing)
        try:
            from email_validator import validate_email
            validate_email(v, check_deliverability=False)  # Don't check if domain exists
            return v
        except Exception:
            # Fallback to basic email format validation
            import re
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                return v
            raise ValueError('Invalid email format')

class UserProfile(BaseModel):
    name: str
    age: Optional[int] = None
    date_of_birth: Optional[str] = None
    current_strategy: Optional[str] = None
    anonymous: bool = False

class AuthService:
    """Authentication service using Supabase Auth with service role"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url or not self.anon_key:
            raise ValueError("Missing Supabase credentials in environment variables")
        
        # Client for normal operations (uses anon key)
        self.client: Client = create_client(self.url, self.anon_key)
        
        # Service client for profile creation (uses service role key)
        self.service_client: Client = create_client(self.url, self.service_key) if self.service_key else None
    
    async def register_user(self, user_data: UserRegistration) -> Dict[str, Any]:
        """
        Register a new user with email and password
        
        Args:
            user_data: User registration data
            
        Returns:
            User data and session information
        """
        try:
            # Register user with Supabase Auth (using anon client)
            auth_response = self.client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "name": user_data.name,
                        "age": user_data.age,
                        "date_of_birth": user_data.date_of_birth,
                        "anonymous": user_data.anonymous
                    }
                }
            })
            
            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account"
                )
            
            # Always create/update profile using service client to bypass RLS
            profile_data = {
                "user_id": auth_response.user.id,
                "date_of_birth": user_data.date_of_birth if user_data.date_of_birth and user_data.date_of_birth.strip() else None,
                "dietary_preferences": user_data.dietary_preferences if hasattr(user_data, 'dietary_preferences') else [],
                "cycle_length": user_data.cycle_length if hasattr(user_data, 'cycle_length') else None,
                "consent": True,
                "anonymous": user_data.anonymous
            }
            
            if self.service_client:
                # Use upsert to handle both insert and update cases
                # This will insert if not exists, update if exists
                profile_result = self.service_client.table('profiles').upsert(profile_data).execute()
            else:
                # Fallback to regular client (may fail due to RLS)
                profile_result = self.client.table('profiles').upsert(profile_data).execute()
            
            return {
                "success": True,
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "name": user_data.name,
                    "age": user_data.age,
                    "date_of_birth": user_data.date_of_birth if user_data.date_of_birth and user_data.date_of_birth.strip() else None,
                    "anonymous": user_data.anonymous
                },
                "session": {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_at": auth_response.session.expires_at
                },
                "email_confirmation_required": False,
                "message": "Registration successful! You can now continue with your health journey."
            }
            
        except Exception as e:
            # Handle specific Supabase errors
            error_message = str(e)
            if "User already registered" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email already exists. Please try logging in instead."
                )
            elif "Password should be at least" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must be at least 6 characters long."
                )
            elif "Invalid email" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please enter a valid email address."
                )
            elif "duplicate key value violates unique constraint" in error_message:
                # This happens when the user profile already exists (created by trigger)
                # This is actually a success case - user was created, profile exists
                return {
                    "success": True,
                    "user": {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                        "name": user_data.name,
                        "age": user_data.age,
                        "date_of_birth": user_data.date_of_birth if user_data.date_of_birth and user_data.date_of_birth.strip() else None,
                        "anonymous": user_data.anonymous
                    },
                    "session": None,  # No session until email is confirmed
                    "email_confirmation_required": True,
                    "message": "Registration successful! Please check your email and click the confirmation link to complete your account setup."
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Registration failed: {error_message}"
                )
    
    async def login_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """
        Login user with email and password
        
        Args:
            login_data: User login credentials
            
        Returns:
            User data and session information
        """
        try:
            # Login user with Supabase Auth
            auth_response = self.client.auth.sign_in_with_password({
                "email": login_data.email,
                "password": login_data.password
            })
            
            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Check if user's email is confirmed
                        # Email confirmation is no longer required
            
            # Get user profile using service client (bypasses RLS)
            if self.service_client:
                profile_result = self.service_client.table('profiles').select('*').eq('user_id', auth_response.user.id).execute()
            else:
                profile_result = self.client.table('profiles').select('*').eq('user_id', auth_response.user.id).execute()
            
            if not profile_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            profile = profile_result.data[0]
            
            return {
                "success": True,
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "name": profile.get('name'),
                    "age": profile.get('age'),
                    "date_of_birth": profile.get('date_of_birth'),
                    "anonymous": profile.get('anonymous', False)
                },
                "session": {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_at": auth_response.session.expires_at
                },
                "message": "Login successful"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            error_message = str(e)
            if "Invalid login credentials" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            elif "Email not confirmed" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please check your email and click the confirmation link to verify your account before logging in."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Login failed: {error_message}"
                )
    
    async def logout_user(self, access_token: str) -> Dict[str, Any]:
        """
        Logout user and invalidate session
        
        Args:
            access_token: User's access token
            
        Returns:
            Logout confirmation
        """
        try:
            # Secure logout: Invalidate session on server side
            # Set the session for the client to ensure proper cleanup
            self.client.auth.set_session(access_token, "")
            
            # Sign out the user - this invalidates the session
            self.client.auth.sign_out()
            
            return {
                "success": True,
                "message": "Logout successful"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Logout failed: {str(e)}"
            )
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile by ID
        
        Args:
            user_id: User's UUID
            
        Returns:
            User profile data
        """
        try:
            if self.service_client:
                result = self.service_client.table('profiles').select('*').eq('user_id', user_id).execute()
            else:
                result = self.client.table('profiles').select('*').eq('user_id', user_id).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            profile = result.data[0]
            
            return {
                "success": True,
                "profile": {
                    "id": profile['id'],
                    "name": profile.get('name'),
                    "age": profile.get('age'),
                    "date_of_birth": profile.get('date_of_birth'),
                    "current_strategy": profile.get('current_strategy'),
                    "anonymous": profile.get('anonymous', False),
                    "created_at": profile.get('created_at'),
                    "updated_at": profile.get('updated_at')
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user profile: {str(e)}"
            )
    
    async def update_user_profile(self, user_id: str, profile_data: UserProfile) -> Dict[str, Any]:
        """
        Update user profile
        
        Args:
            user_id: User's UUID
            profile_data: Updated profile data
            
        Returns:
            Updated profile data
        """
        try:
            update_data = {
                "name": profile_data.name,
                "age": profile_data.age,
                "date_of_birth": profile_data.date_of_birth,
                "current_strategy": profile_data.current_strategy,
                "anonymous": profile_data.anonymous
            }
            
            if self.service_client:
                result = self.service_client.table('profiles').update(update_data).eq('user_id', user_id).execute()
            else:
                result = self.client.table('profiles').update(update_data).eq('user_id', user_id).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            return {
                "success": True,
                "profile": result.data[0],
                "message": "Profile updated successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update profile: {str(e)}"
            )
    
    async def verify_token(self, access_token: str) -> Dict[str, Any]:
        """
        Verify user's access token
        
        Args:
            access_token: User's access token
            
        Returns:
            Token verification result
        """
        try:
            # Set the session for the client
            self.client.auth.set_session(access_token, "")
            
            # Get the current user
            user = self.client.auth.get_user()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            return {
                "success": True,
                "user_id": user.id,
                "email": user.email,
                "email_confirmed": bool(user.email_confirmed_at),
                "message": "Token is valid"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
    
    async def resend_confirmation_email(self, email: str) -> Dict[str, Any]:
        """Deprecated: Email confirmation is no longer required"""
        return {
            "success": False,
            "message": "Email confirmation is no longer required for this app."
        }
    
    async def reset_password(self, email: str) -> Dict[str, Any]:
        """
        Send password reset email to user
        
        Args:
            email: User's email address
            
        Returns:
            Password reset email status
        """
        try:
            # Send password reset email
            result = self.client.auth.reset_password_email(email)
            
            return {
                "success": True,
                "message": "Password reset email sent successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send password reset email: {str(e)}"
            }

# Create global auth service instance
auth_service = AuthService()