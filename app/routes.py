from app import app
from flask import render_template, redirect, url_for, request, session, flash
from app import app, db, login_manager
from app.models import User, Flower, Contact, Blog, Wishlist, Cart, Order, OrderItem, Rating
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField
from werkzeug.utils import secure_filename
import os 


login_manager.login_view = "login"

class CustomAdminIndex(AdminIndexView): 
    @expose('/')
    def index(self):
        if not self.auth():
            return redirect(url_for("admin_login"))
        return super(CustomAdminIndex, self).index()
    
    def auth(self):
        return session.get("admin_logged_in") 

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session["admin_logged_in"] = True
            return redirect('/admin')
        else:
            return render_template('admin_login.html', error="Admin login failed.") 
    return render_template('admin_login.html')

@app.route('/delivery/login', methods=['GET', 'POST'])
def delivery_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'delivery' and password == 'deliverypass':
            session["delivery_logged_in"] = True
            return redirect(url_for('delivery_orders'))
        else:
            return render_template('delivery_login.html', error="Delivery login failed.") 
    return render_template('delivery_login.html')

@app.route('/delivery/logout')
def delivery_logout():
    session.pop("delivery_logged_in", None)
    return redirect(url_for('delivery_login'))

@app.route('/delivery/orders')
def delivery_orders():
    if not session.get("delivery_logged_in"):
        return redirect(url_for('delivery_login'))
    shipped_orders = Order.query.filter_by(status='Shipped').order_by(Order.date_created.desc()).all()
    return render_template('delivery_orders.html', orders=shipped_orders)

@app.route('/delivery/update_order/<int:order_id>', methods=['POST'])
def delivery_update_order(order_id):
    if not session.get("delivery_logged_in"):
        return redirect(url_for('delivery_login'))
    order = Order.query.get_or_404(order_id)
    if order.status != 'Shipped':
        flash("This order is not ready for delivery.", "danger")
        return redirect(url_for('delivery_orders'))
    order.status = 'Delivered'
    db.session.commit()
    return redirect(url_for('delivery_orders'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    user = False 
    if current_user.is_authenticated:
        user = current_user
    return render_template("index.html", user=user)

@app.route('/products/')
@app.route('/products/<category>')
def products(category="all"):
    if category == 'all':
        flowers = Flower.query.all()
    else:
        flowers = Flower.query.filter(Flower.category.like(f'%{category}%')).all()
    return render_template('products.html', flowers=flowers, category=category)

@app.route('/product/<id>') 
def product(id):
    product = Flower.query.filter_by(id=int(id)).first_or_404()
    return render_template('product.html', product=product)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first() 
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next') or url_for('home')
            return redirect(next_page)
        else:
            return redirect(url_for('home', invalid=True, show_login=True))
    return redirect(url_for('home', invalid=request.args.get('invalid'), show_login=True))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        if password != cpassword:
            return redirect(url_for('home', passwordmismatch=True, show_register=True))
        username = email.split('@')[0]
        if User.query.filter_by(email=email).first():
            return redirect(url_for('home', userexists=True, show_register=True))
        hashed_password = generate_password_hash(password)
        user = User(
            name=f'{firstname} {lastname}', 
            email=email,
            username=username,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home', show_login=True))
    return redirect(url_for('home', userexists=request.args.get('userexists'), passwordmismatch=request.args.get('passwordmismatch'), show_register=True))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home')) 

@app.route('/blogs/')
def blogs():
    blog_posts = Blog.query.all()
    return render_template('blogs.html', blog_posts=blog_posts)

@app.route('/blog/<id>')
def blog(id):
    blog_post = Blog.query.filter_by(id=int(id)).first_or_404()
    return render_template('blog.html', blog_post=blog_post)

@app.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_created.desc()).all()
    for order in orders:
        if order.status == 'Delivered':
            order.has_unreviewed = any(
                Rating.query.filter_by(user_id=current_user.id, flower_id=item.flower_id).first() is None
                for item in order.items
            )
        else:
            order.has_unreviewed = False
    return render_template('profile.html', orders=orders)

admin = Admin(app, index_view=CustomAdminIndex(), name='Petals Admin', template_mode='bootstrap3') 

class CustomModelView(ModelView): 
    def is_accessible(self):
        return session.get("admin_logged_in")
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

admin.add_view(CustomModelView(User, db.session))
admin.add_view(CustomModelView(Contact, db.session))

class FlowerModelView(ModelView):
    form_excluded_columns = ['image_url', 'ratings']
    def is_accessible(self):
        return session.get("admin_logged_in")
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))
    def scaffold_form(self):
        form_class = super(FlowerModelView, self).scaffold_form()
        form_class.image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jfif', 'jpeg'], 'Images only!')])
        return form_class
    def on_model_change(self, form, model, is_created):
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(file_path)
            model.image_url = filename

admin.add_view(FlowerModelView(Flower, db.session))
admin.add_view(FlowerModelView(Blog, db.session))

class OrderModelView(ModelView):
    column_list = ['id', 'user.email', 'phone', 'address', 'status', 'date_created', 'items']
    form_excluded_columns = ['items', 'user']
    form_edit_rules = ['user_email', 'phone', 'address', 'date_created', 'items_display', 'status']
    form_widget_args = {
        'user_email': {'readonly': True},
        'phone': {'readonly': True},
        'address': {'readonly': True},
        'date_created': {'readonly': True},
        'items_display': {'readonly': True}
    }
    form_overrides = {
        'date_created': StringField,
        'status': SelectField
    }
    form_extra_fields = {
        'user_email': StringField('User Email'),
        'items_display': StringField('Items'),
        'status': SelectField('Status', choices=[('Processing', 'Processing'), ('Shipped', 'Shipped')])
    }
    column_formatters = {
        'items': lambda v, c, m, p: ', '.join([f"{item.flower.name} (x{item.quantity})" for item in m.items]),
        'user.email': lambda v, c, m, p: m.user.email if m.user else ''
    }
    def is_accessible(self):
        return session.get("admin_logged_in")
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))
    def is_editable(self, model_id):
        order = Order.query.get(model_id)
        return order and order.status != 'Delivered'
    def on_form_prefill(self, form, id):
        order = Order.query.get(id)
        if order:
            form.items_display.data = ', '.join([f"{item.flower.name} (x{item.quantity})" for item in order.items])
            form.user_email.data = order.user.email if order.user else ''
            form.phone.data = order.phone
            form.address.data = order.address
            form.date_created.data = str(order.date_created)
            form.status.data = order.status
        return form
    def update_model(self, form, model):
        try:
            model.status = form.status.data
            self.session.commit()
            return True
        except Exception as ex:
            flash(f"Failed to update order: {str(ex)}", 'error')
            return False

admin.add_view(OrderModelView(Order, db.session))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form.get('email')
        message = request.form.get('message')
        contact = Contact(email=email, message=message)
        db.session.add(contact)
        db.session.commit()
        return render_template('thankscontact.html')
    return render_template('contact.html')

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        searchbar = request.form.get('searchbar')
        flowers = Flower.query.filter(Flower.name.like(f'%{searchbar}%')).all()
        return render_template('search.html', flowers=flowers, category=searchbar)
        
@app.route('/subscribe', methods=['POST'])
def subscribe():
    return render_template('tnx.html')

@app.route('/no_socialmedia')
def no_socialmedia():
    return render_template('no_socials.html')

@app.route('/about')
def about():
    return render_template('aboutus.html')

@app.route('/wishlist')
@login_required
def wishlist():
    wishlist_entries = Wishlist.query.filter_by(user_id=current_user.id).all()
    products = [entry.flower for entry in wishlist_entries]
    return render_template('wishlist.html', products=products)

@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/wishlist/toggle/<int:flower_id>')
@login_required
def toggle_wishlist(flower_id):
    item = Wishlist.query.filter_by(user_id=current_user.id, flower_id=flower_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    else:
        new_item = Wishlist(user_id=current_user.id, flower_id=flower_id)
        db.session.add(new_item)
        db.session.commit()
    return redirect(request.referrer or url_for('home'))

@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    product = Flower.query.get_or_404(product_id)
    if product.stock < quantity:
        flash("Not enough product stock available.", "danger")
        return redirect(request.referrer or url_for('product', id=product_id))
    cart_item = Cart.query.filter_by(user_id=current_user.id, flower_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=current_user.id, flower_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    db.session.commit()
    flash("Product added to cart.", "success")
    return redirect(url_for('cart'))

@app.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    action = request.form.get('action')
    cart_item = Cart.query.get_or_404(cart_id)
    if cart_item.user_id != current_user.id:
        return redirect(url_for('cart'))
    if action == "delete":
        cart_item.flower.stock += cart_item.quantity
        db.session.delete(cart_item)
    if action == "increase":
        if cart_item.flower.stock > 0:
            cart_item.quantity += 1
            cart_item.flower.stock -= 1
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.flower.stock += 1
        else:
            cart_item.flower.stock += cart_item.quantity
            db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/checkout')
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty.", "danger")
        return redirect(url_for('cart'))
    return render_template('checkout.html', cart_items=cart_items)

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    phone = request.form.get('phone')
    address = request.form.get('address')
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty.", "danger")
        return redirect(url_for('cart'))
    order = Order(
        user_id=current_user.id,
        phone=phone,
        address=address,
        status='Processing'
    )
    db.session.add(order)
    for item in cart_items:
        order_item = OrderItem(
            order=order,
            flower_id=item.flower_id,
            quantity=item.quantity,
            price=item.flower.price
        )
        db.session.add(order_item)
        item.flower.stock -= item.quantity
        db.session.delete(item)
    db.session.commit()
    flash("Order placed successfully!", "success")
    return redirect(url_for('order_confirmation'))

@app.route('/order_confirmation')
@login_required
def order_confirmation():
    return render_template('order_confirmation.html')

@app.route('/review_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def review_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id or order.status != 'Delivered':
        flash("Invalid access.", "danger")
        return redirect(url_for('profile'))
    unreviewed_items = [item for item in order.items if not Rating.query.filter_by(user_id=current_user.id, flower_id=item.flower_id).first()]
    if not unreviewed_items:
        flash("All items in this order have been reviewed.", "info")
        return redirect(url_for('profile'))
    if request.method == 'POST':
        for item in unreviewed_items:
            flower_id = item.flower_id
            rating_key = f'rating_{flower_id}'
            review_key = f'review_{flower_id}'
            if rating_key in request.form:
                try:
                    rating_val = int(request.form[rating_key])
                    review_text = request.form.get(review_key, '').strip()
                    if 1 <= rating_val <= 5:
                        new_rating = Rating(
                            user_id=current_user.id,
                            flower_id=flower_id,
                            rating=rating_val,
                            review_text=review_text if review_text else None
                        )
                        db.session.add(new_rating)
                    else:
                        flash(f"Invalid rating for {item.flower.name}.", "danger")
                except ValueError:
                    flash(f"Invalid rating value for {item.flower.name}.", "danger")
        db.session.commit()
        flash("Reviews submitted successfully!", "success")
        return redirect(url_for('profile'))
    return render_template('review_order.html', order=order, unreviewed_items=unreviewed_items)