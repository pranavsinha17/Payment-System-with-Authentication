from pydantic_settings import BaseSettings

class RazorpaySettings(BaseSettings):
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    
    class Config:
        env_file = ".env"
        extra = "allow"  # This allows extra fields in the settings

razorpay_settings = RazorpaySettings() 