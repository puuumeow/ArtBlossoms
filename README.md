# ArtBlossoms

**ArtBlossoms** is a sleek, web-based platform connecting artists and art enthusiasts. Artists can display and sell their creations, while buyers can browse, purchase, and request custom artworks. The platform emphasizes usability, visual appeal, and seamless interaction for all users.

---

## Features

### Artists

* Upload and manage artwork with images, descriptions, and categories.
* Receive instant notifications for new orders.
* Handle custom artwork requests efficiently.
* Track order statuses and view buyer messages.

### Buyers

* Browse and filter artworks by category, artist, or tags.
* Add items to a cart and place bulk orders.
* Track order statuses easily.
* Submit reviews for purchased artworks.

### Users with Both Roles

* Access all features for artists and buyers.
* Dynamic profile pages displaying role-specific sections.

---

## Technologies

* **Backend:** Python, Flask
* **Database:** MySQL
* **Frontend:** HTML, CSS, JavaScript
* **Additional Tools:** Bootstrap (optional), Jinja2 templating

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/puuumeow/ArtBlossoms.git
```

2. Enter the project directory:

```bash
cd ArtBlossoms
```

3. (Optional) Create a virtual environment:

```bash
python -m venv venv
```

4. Activate the virtual environment:

* **Windows:**

```bash
venv\Scripts\activate
```

* **Mac/Linux:**

```bash
source venv/bin/activate
```

5. Install required packages:

```bash
pip install flask mysql-connector-python
```

Or with a `requirements.txt`:

```bash
pip install -r requirements.txt
```

6. Set up the MySQL database:

* Create a database named `ArtBlossoms`.
* Import the provided schema or create tables manually.

7. Run the application:

```bash
python app.py
```

8. Open your browser and visit:

```
http://127.0.0.1:5000/
```

---

## Database Overview

* **users:** User info, roles, and profiles.
* **artworks:** Artwork details, categories, and prices.
* **orders:** Buyer orders, messages, and status tracking.
* **carts:** Stores items added to carts.
* **reviews:** Buyer reviews of purchased artwork.
* **order\_notifications:** Alerts for artists on new orders.
* **categories, tags, artwork\_tags, districts:** Organize artworks by category, tag, and location.

---

## Project Structure

```
ArtBlossoms/
├─ app.py
├─ db.py
├─ requirements.txt
├─ routes/
│  ├─ artwork_route.py
│  ├─ browse_artworks_route.py
│  ├─ cart_route.py
│  ├─ home_route.py
│  ├─ login_route.py
│  ├─ logout_route.py
│  ├─ order_route.py
│  ├─ profile_route.py
│  ├─ register_route.py
│  ├─ review_route.py
│  └─ upload_artwork_route.py
├─ templates/
│  ├─ home.html
│  ├─ login.html
│  ├─ register.html
│  ├─ profile.html
│  ├─ artwork_detail.html
│  └─ ...
└─ static/
   ├─ images/
   ├─ css/
   └─ js/
```

---

## Future Enhancements

* Real-time chat between buyers and artists.
* Payment gateway integration.
* Artwork auctions and bidding system.
* Advanced analytics for artists (views, sales, statistics).

---


## Copyright

Copyright Notice

© 2025 [Laiba Sumaiya Nazim]. All rights reserved. This project is strictly for educational purposes and may not be copied, reproduced, or redistributed in any form without explicit permission.
