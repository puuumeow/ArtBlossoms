# ArtBlossoms

**ArtBlossoms** is a modern web-based platform for artists and buyers. Artists can showcase and sell their artwork, while buyers can browse, purchase, and request custom art pieces. The platform focuses on ease of use, visual appeal, and a seamless experience for both artists and buyers.

---

## Features

### For Artists
- Upload and manage artworks with images, descriptions, and categories.
- Receive notifications when orders are placed.
- Manage custom artwork requests.
- Track order status and view buyer messages.

### For Buyers
- Browse all artworks with search and filtering options.
- Add artworks to cart and place bulk orders.
- Track order status.
- Leave reviews on purchased artworks.

### For Users with Both Roles
- Full access to artist and buyer functionalities.
- Dynamic profile page showing relevant sections based on role.

---

## Technologies Used
- **Backend:** Python, Flask  
- **Database:** MySQL  
- **Frontend:** HTML, CSS, JavaScript  
- **Other Tools:** Bootstrap (optional for styling), Jinja2 templating  

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ArtBlossoms.git

    Navigate to the project folder:

cd ArtBlossoms

(Optional but recommended) Create a virtual environment:

python -m venv venv

Activate the virtual environment:

    Windows:

venv\Scripts\activate

Mac/Linux:

    source venv/bin/activate

Install required Python packages:

pip install flask mysql-connector-python

    Or, if a requirements.txt file is provided:

pip install -r requirements.txt

Set up the MySQL database:

    Create a database named ArtBlossoms.

    Import the provided schema or manually create tables as defined in the project.

Run the Flask application:

python app.py

Open your browser and go to:

    http://127.0.0.1:5000/

Database Schema Overview

    users: Stores user info, roles, and profile details.

    artworks: Stores artwork details, images, categories, and prices.

    orders: Tracks orders, buyer details, messages, and status.

    carts: Stores artworks added to the cart by buyers.

    reviews: Buyer reviews for purchased artworks.

    order_notifications: Notifies artists of new orders.

    categories, tags, artwork_tags, districts: Support for categorization, tagging, and location-based details.

Project Structure

ArtBlossoms/
│
├─ app.py
├─ db.py
├─ requirements.txt
├─ routes/
│   ├─ artwork_route.py
│   ├─ browse_artworks_route.py
│   ├─ cart_route.py
│   ├─ home_route.py
│   ├─ login_route.py
│   ├─ logout_route.py
│   ├─ order_route.py
│   ├─ profile_route.py
│   ├─ register_route.py
│   ├─ review_route.py
│   └─ upload_artwork_route.py
│
├─ templates/
│   ├─ home.html
│   ├─ login.html
│   ├─ register.html
│   ├─ profile.html
│   ├─ artwork_detail.html
│   └─ ...
│
└─ static/
    ├─ images/
    ├─ css/
    └─ js/

Future Enhancements

    Real-time chat between buyers and artists.

    Payment gateway integration.

    Artwork bidding and auction system.

    Enhanced analytics for artists (views, sales stats, etc.).

License

This project is licensed under the MIT License.
Copyright

© 2025 [Laiba Sumaiya Nazim]. All rights reserved.
Unauthorized copying, reproduction, or distribution of this project, in whole or in part, is prohibited.
