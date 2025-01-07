PhotoShare Project
PhotoShare is a photo-sharing web application built with FastAPI. It allows users to upload photos, comment on them, and interact with other users in a manner similar to Instagram. The application includes different user roles, secure authentication, and flexible functionalities for managing photos, comments, and more.

PhotoShare is designed as an Instagram-like platform, where users can:

Upload photos to their personal profile or share with others.
Like and comment on photos.
Have user roles such as admin, regular user, etc.
Manage accounts with secure login and registration via JWT tokens.
View personalized photo galleries and user profiles.
Built with FastAPI, this application ensures fast responses and seamless scalability. It also employs best practices for security and modularity.

Features
User Roles:
Different roles, such as admin and regular user, are implemented with distinct permissions. Admins can manage users and moderate content.

Photo Management:
Users can upload, update, delete, and view photos. Each photo can have metadata, including tags and descriptions.

Comments and Likes:
Users can comment on and like photos, enhancing interaction.

Authentication:
Secure user authentication using JWT tokens for login sessions.

Image Upload:
Supports photo uploads with automatic resizing and format conversion.

User Profiles:
Each user has a profile displaying their uploaded photos, bio, and account details.

Pagination and Search:
Efficient pagination for photo galleries and search by tags, categories, or usernames.

Tech Stack
Backend:

FastAPI (Asynchronous web framework for building APIs)
SQLAlchemy (ORM for database interactions)
PostgreSQL (Database for storing users, photos, comments, etc.)
Pydantic (Data validation and serialization)
JWT (Authentication using JSON Web Tokens)
Alembic (Database migrations)
Uvicorn (ASGI server for FastAPI)

Deployment:
Docker (for containerization)
GitHub Actions (CI/CD pipeline)
AWS / Heroku (for deployment)

Getting Started
Prerequisites
Ensure you have the following tools installed on your system:
Python 3.8+: Download here
PostgreSQL (or you can use a cloud-based service like Heroku PostgreSQL)
Docker (for containerization, optional but recommended for consistency)
Node.js and npm (for running the frontend if you want to modify or build the UI)
Installation
Follow these steps to set up the project locally:

Clone the repository:
git clone https://github.com/Mykyta-Harashchenko/PhotoShare_Project.git

Navigate to the project folder:
cd PhotoShare_Project

Install the required dependencies:
pip install -r requirements.txt

Set up environment variables: Create a .env file in the backend folder and add the following:
DATABASE_URL=postgresql://username:password@localhost:5432/photoshare
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

Database Setup:
Set up the PostgreSQL database:
alembic upgrade head
Run the application:

Start the backend server:
uvicorn photoshare.main:app --reload

The backend should be accessible at http://localhost:8000.

API Endpoints
Here are the key API endpoints for interacting with the PhotoShare platform:

Authentication
POST /auth/signup
Register a new user.

POST /auth/login
Authenticate and retrieve a JWT token.

User Management
GET /users/me
Get the current authenticated user's information.

PUT /users/me
Update the current user's profile (e.g., bio, profile picture).

Photos
POST /photos
Upload a new photo.

GET /photos
Retrieve a list of photos with pagination.

GET /photos/{photo_id}
View a single photo.

PUT /photos/{photo_id}
Edit an existing photo.

DELETE /photos/{photo_id}
Delete a photo.

Comments
POST /photos/{photo_id}/comments
Post a new comment on a photo.

GET /photos/{photo_id}/comments
Get all comments for a specific photo.

Likes
POST /photos/{photo_id}/like
Like a photo.

DELETE /photos/{photo_id}/like
Unlike a photo.

Usage
Once your server is running, you can interact with the app at http://localhost:8000/docs, by Swagger. Here's how you can use it:

Sign Up: Create a new account by registering with your email.
Login: Authenticate with your email and password.
Upload Photos: Add new photos to your gallery.
View Photos: Browse photos uploaded by you and other users.
Comment & Like: Engage with photos by commenting and liking them.
Profile: Edit and view your personal profile and gallery.
Contributing
We welcome contributions to the PhotoShare Project! Here's how you can contribute:

Fork the repository.
Create a feature branch (git checkout -b feature-name).
Make your changes and ensure they are well-tested.
Commit your changes (git commit -am 'Add new feature').
Push to your forked repository (git push origin feature-name).
Open a pull request to the dev branch of the main repository.
Please ensure your code adheres to our style guide and passes all tests before submitting a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
For any questions or issues, feel free to contact us:

GitHub: https://github.com/Mykyta-Harashchenko
Thank you for exploring the PhotoShare Project! We hope you enjoy contributing to and using the platform. Happy coding! 🚀

