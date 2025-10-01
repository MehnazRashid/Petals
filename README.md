# Petals – Online Flower Shop  

**Petals** is a simple e-commerce web application where customers can buy flowers online. Users can browse different flowers, add them to wishlist or cart, place orders, and read blogs about flowers and floral care. Admins can manage products, orders, blogs, and messages from customers.  


## Features  

- User registration and login  
- Browse flowers by category  
- Search products by keywords  
- Add products to wishlist or cart 
- Checkout and place orders (Cash on Delivery)  
- View order history & delivery status  
- Read blogs about flowers  
- Leave reviews and ratings on products  
- Contact admin via contact form  
- Admin panel to manage products, orders, blogs, and users  
- Delivery panel for order updates  



## Tech Stack  

**Backend:**  
- Python 3.13.7  
- Flask (Micro web framework)  
- Flask SQLAlchemy (ORM for database)  
- Flask-Login (Authentication)  
- Flask-WTF (Forms)  
- Flask-Admin (Admin Panel)  
- Werkzeug (Password hashing)  
- Jinja2 (Templating engine)  

**Frontend:**  
- HTML, CSS, JavaScript  
- Bootstrap (UI components)  
- jQuery (Modal support)  
- Font Awesome (Icons)  
- Google Fonts  

**Database:**  
- SQLite (lightweight relational database)  


## Project Structure  

- `Petals/`
  - `static/` – CSS, images, uploads, JS
  - `templates/` – HTML files (Jinja2 templates)
  - `models.py` – Database models
  - `routes.py` – Backend routes & logic
  - `__init__.py` – App initialization


## Accessing Admin & Delivery Panel  

### Admin Panel  
- Go to: `http://127.0.0.1:5000/admin`  
- Login credentials:  
  - **Username:** `admin`  
  - **Password:** `password`  

### Delivery Panel  
- Go to: `http://127.0.0.1:5000/delivery-login`  
- Login credentials:  
  - **Username:** `delivery`  
  - **Password:** `deliverypass`  


### Future Improvements 
- Implement online payment methods
- Make the website fully mobile-responsive
- Enhance design & visual appeal
- Add email verification for secure accounts
- Deploy the website for real use
- Create a separate delivery application and connect it to the system

