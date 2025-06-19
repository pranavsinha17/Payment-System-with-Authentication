# Payment System with Authentication

A FastAPI-based payment system with user authentication, subscription management, and product selection capabilities.

## Latest Features & Security Updates

### 1. 30-Day Free Trial for First-Time Users
- First-time users automatically receive a 30-day free trial with access to all products.
- The system tracks trial usage and prevents multiple trials per user.

### 2. Prevent Multiple Active Subscriptions
- Users cannot create a new subscription if they already have an active one.
- Attempting to do so returns a clear error message.

### 3. Cookie-Based Authentication
- JWT tokens are now set as HTTP-only cookies on login for secure frontend authentication.
- The backend reads tokens from cookies or headers, supporting modern frontend best practices.
- CORS is configured to allow credentials.

### 4. Password Reset Flow (with Email)
- Users can request a password reset link via `/users/forgot-password` (POST, JSON: `{ "email": "user@example.com" }`).
- A secure reset link is emailed using SendGrid (configure your API key and sender email).
- Users reset their password via `/users/reset-password` (POST, JSON: `{ "token": "...", "new_password": "..." }`).

### 5. Token Invalidation After Password Reset
- After a password reset, all previously issued tokens are invalidated.
- This is achieved by tracking `last_password_change` in the database and JWT. If a token's value doesn't match the DB, access is denied and the user must log in again.
- **Manual DB update required:**
  ```sql
  ALTER TABLE user
  ADD COLUMN last_password_change DATETIME DEFAULT CURRENT_TIMESTAMP;
  ```

---

## Features

- User Authentication (JWT-based)
- Subscription Management
- Product Selection
- Payment Processing
- Role-based Access Control

## Prerequisites

- Python 3.8+
- MySQL Database
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd payment-system-with-authentication
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
# Azure SQL Configuration
AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=your-database
AZURE_SQL_USERNAME=your-username
AZURE_SQL_PASSWORD=your-password

# Application Configuration
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Install ODBC Driver:
Before running the application, make sure to install the ODBC Driver for SQL Server:
- Windows: Download and install from Microsoft's website
- Linux: Follow Microsoft's instructions for your distribution
- macOS: Use Homebrew: `brew tap microsoft/mssql-release && brew install msodbcsql18`

6. Initialize the database:
```bash
alembic upgrade head
```

## Running the Application

Start the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Response Format

All API endpoints return responses in a consistent, industry-standard format:

### Success Response
```
{
  "success": true,
  "data": ... // resource, list, or message
}
```
- For list endpoints, `data` is an array.
- For actions/messages, `data` contains a `message` field.
- For resource creation or retrieval, `data` contains the resource or list.

### Error Response
```
{
  "success": false,
  "error": {
    "type": "ExceptionType",
    "message": "Error message",
    "code": 400
  }
}
```

## API Endpoints

### Authentication

#### Register User
```http
POST /users/register
Content-Type: application/json

{
    "email": "user@example.com",
    "phone": "1234567890",
    "password": "yourpassword"
}
```

#### Login
```http
POST /users/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "yourpassword"
}
```

### Subscription Management

#### Create Subscription Plan
```http
POST /subscriptions/subscription-plans
Content-Type: application/json

{
    "name": "Yearly Plan",
    "price": 200.0,
    "duration": "yearly",
    "product_ids": ["product1", "product2", "product3"]
}
```

#### Create User Subscription
```http
POST /subscriptions/user-subscriptions
Content-Type: application/json

{
    "plan_id": "plan-id",
    "start_date": "2024-03-20T10:00:00",
    "end_date": "2024-04-20T10:00:00"
}
```

#### Get User Subscriptions
```http
GET /subscriptions/me/subscriptions
Authorization: Bearer <token>
```

#### Get Active Subscription
```http
GET /subscriptions/me/active-subscription
Authorization: Bearer <token>
```

### Product Management

#### Create Product
```http
POST /subscriptions/products
Content-Type: application/json

{
    "id": "product1",
    "name": "Product 1",
    "description": "Description of Product 1",
    "type": "type1",
    "script_ref": "script1",
    "output_type": "output1"
}
```

#### Select Products for Subscription
```http
POST /subscriptions/product-selections
Content-Type: application/json

{
    "subscription_id": "subscription-id",
    "product_ids": ["product1", "product2", "product3"]
}
```

#### Get Product Selections
```http
GET /subscriptions/subscriptions/{subscription_id}/product-selections
Authorization: Bearer <token>
```

### Payment Processing

#### Create Payment
```http
POST /subscriptions/payments
Content-Type: application/json

{
    "subscription_id": "subscription-id",
    "razorpay_payment_id": "payment-id",
    "amount": 200.0,
    "status": "completed",
    "paid_at": "2024-03-20T10:00:00"
}
```

#### Get Payment History
```http
GET /subscriptions/payments
Authorization: Bearer <token>
```

## Database Schema

### Users
- id (UUID)
- email
- phone
- password_hash
- is_active
- registered_at

### Subscription Plans
- id (UUID)
- name
- price
- duration
- product_ids
- created_at

### User Subscriptions
- id (UUID)
- user_id
- plan_id
- start_date
- end_date
- is_active
- created_at

### Product Selections
- id (UUID)
- user_id
- subscription_id
- product_id
- is_active
- created_at
- updated_at

### Products
- id (UUID)
- name
- description
- type
- script_ref
- output_type

### Payments
- id (UUID)
- subscription_id
- razorpay_payment_id
- amount
- status
- paid_at
- created_at

## Security

- JWT-based authentication
- Password hashing using bcrypt
- Role-based access control
- Secure password storage

## Error Handling

- All errors are returned in a consistent format as shown above.
- Standard HTTP status codes are used (400, 401, 403, 404, 409, 422, 500, etc.).
- Error responses include an error type, message, and code for easy client-side handling.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 