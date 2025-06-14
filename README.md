# Payment System with Authentication

A FastAPI-based payment system with user authentication, subscription management, and product selection capabilities.

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
DATABASE_URL=mysql+pymysql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Initialize the database:
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
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
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

The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 