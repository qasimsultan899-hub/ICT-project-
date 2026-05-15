import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

# ==========================================
# 1. PAGE CONFIGURATION & INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="Jerry Shoes Outlet",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State for Product Catalog
if "products" not in st.session_state:
    st.session_state.products = [
        {"id": "1", "name": "Air Max Classic", "brand": "Nike", "price": 18500, "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500", "available": True},
        {"id": "2", "name": "Ultraboost 22", "brand": "Adidas", "price": 22000, "image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500", "available": True},
        {"id": "3", "name": "Classic Leather", "brand": "Reebok", "price": 12500, "image": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=500", "available": False},
        {"id": "4", "name": "Speedcross 5", "brand": "Salomon", "price": 19500, "image": "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=500", "available": True}
    ]

# Initialize Session State for Shopping Cart
if "cart" not in st.session_state:
    st.session_state.cart = []

# Initialize Checkout Wizard Step State
if "checkout_step" not in st.session_state:
    st.session_state.checkout_step = 1

# ==========================================
# 2. EMAIL NOTIFICATION SYSTEM (SMTP)
# ==========================================
def send_order_email(order_id, cart_items, total_amount, delivery_method, payment_method, customer_info):
    """Sends an automated email notification to the store owner using Streamlit Secrets."""
    try:
        # Fetch configurations safely from st.secrets
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = int(st.secrets["email"]["smtp_port"])
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]
        receiver_email = st.secrets["email"]["receiver_email"]
        
        # Build the HTML Email content
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 New Order Alert - Jerry Shoes Outlet [#{order_id}]"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        items_html = "".join([
            f"<li><b>{item['name']}</b> ({item['brand']}) - Size: {item['size']} | Rs. {item['price']:,}</li>" 
            for item in cart_items
        ])

        html_content = f"""
        <html>
            <body>
                <h2>👟 New Order Received! (# {order_id})</h2>
                <p><b>Total Amount:</b> Rs. {total_amount:,}</p>
                <p><b>Fulfillment Preference:</b> {delivery_method}</p>
                <p><b>Payment Method:</b> {payment_method}</p>
                <hr/>
                <h3>🛒 Items Ordered:</h3>
                <ul>{items_html}</ul>
                <hr/>
                <h3>👤 Customer Details:</h3>
                <p><b>Name:</b> {customer_info.get('name', 'N/A')}</p>
                <p><b>Phone:</b> {customer_info.get('phone', 'N/A')}</p>
                <p><b>Email:</b> {customer_info.get('email', 'N/A')}</p>
                <p><b>Shipping Address:</b> {customer_info.get('address', 'N/A')}</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        # Connection and transmission
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        st.sidebar.error(f"Notification Error: {e}")
        return False

# ==========================================
# 3. SIDEBAR NAVIGATION & AUTHENTICATION
# ==========================================
st.sidebar.title("👟 Jerry Shoes Outlet")
st.sidebar.markdown("---")

# Navigation Choice
page = st.sidebar.radio("Navigate to:", ["Shop", "Cart", "Contact Us", "Admin Panel Auth"])

# Password Check Layer for Admin Access
is_admin_authenticated = False
if page == "Admin Panel Auth":
    st.sidebar.markdown("---")
    admin_password = st.sidebar.text_input("Enter Admin Password:", type="password")
    if admin_password == st.secrets.get("admin", {}).get("password", "admin_jerry_shoes"):
        is_admin_authenticated = True
        st.sidebar.success("Access Granted!")
    elif admin_password != "":
        st.sidebar.error("Invalid Credentials.")

# ==========================================
# PAGE 1: PRODUCT CATALOG (SHOP PAGE)
# ==========================================
if page == "Shop":
    st.title("🛒 Discover Our Catalog")
    st.write("Welcome to **Jerry Shoes Outlet**. Browse our curated high-performance collection!")
    st.markdown("---")

    # Grid Display Layout (3 Columns per row)
    cols = st.columns(3)
    
    for idx, item in enumerate(st.session_state.products):
        col = cols[idx % 3]
        with col:
            with st.container(border=True):
                # Standard markdown rendering for image blocks
                st.image(item["image"], use_container_width=True)
                st.subheader(item["name"])
                st.caption(f"Brand: {item['brand']}")
                st.markdown(f"### **Rs. {item['price']:,}**")
                
                # Check Availability Logic
                if item["available"]:
                    st.success("🟢 In Stock")
                    if st.button(f"Add to Cart", key=f"add_{item['id']}"):
                        st.session_state.cart.append({
                            "id": item["id"],
                            "name": item["name"],
                            "brand": item["brand"],
                            "price": item["price"],
                            "size": "9"  # Default fallback placeholder size
                        })
                        st.toast(f"🎉 Added {item['name']} to your cart!")
                else:
                    st.error("🔴 Out of Stock")
                    st.info("Sorry, this item is not currently available.")
                    st.button("Add to Cart", key=f"disabled_{item['id']}", disabled=True)

# ==========================================
# PAGE 2: SHOPPING CART & SEQUENTIAL WIZARD
# ==========================================
elif page == "Cart":
    st.title("🛍️ Shopping Cart")
    st.markdown("---")

    if not st.session_state.cart:
        st.info("Your shopping cart is currently empty. Head over to the **Shop** page to add items!")
    else:
        # Display Current Items in Cart
        st.subheader("Items in your order")
        updated_cart = []
        total_amount = 0

        for idx, item in enumerate(st.session_state.cart):
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                with c1:
                    st.markdown(f"**{item['name']}** \n*Brand: {item['brand']}*")
                with c2:
                    # Dynamically allocate shoe sizing metrics
                    selected_size = st.selectbox(f"Size", ["7", "8", "9", "10", "11"], key=f"size_{idx}", index=2)
                    item["size"] = selected_size
                with c3:
                    st.markdown(f"**Rs. {item['price']:,}**")
                with c4:
                    if st.button("🗑️ Remove", key=f"rem_{idx}"):
                        st.session_state.cart.pop(idx)
                        st.rerun()
                
                updated_cart.append(item)
                total_amount += item["price"]

        st.session_state.cart = updated_cart
        
        st.markdown("---")
        st.markdown(f"### **Grand Total Amount: Rs. {total_amount:,}**")
        st.markdown("---")

        # SEQUENTIAL CHECKOUT WIZARD
        st.subheader("📋 Sequential Checkout Process")
        
        # Visual step indicator bar
        step = st.session_state.checkout_step
        st.progress(step / 3, text=f"Step {step} of 3")

        # STEP 1: Fulfillment Preference Choice
        if step == 1:
            st.markdown("#### **Step 1: Order Fulfillment Preference**")
            with st.form("fulfillment_form"):
                delivery_method = st.radio("How would you like to receive your order?", ["Home Delivery", "Pick up from nearest outlet"])
                submit_step1 = st.form_submit_button("Proceed to Payment Method")
                
                if submit_step1:
                    if not st.session_state.cart:
                        st.error("Data Validation Error: Cart is empty. Please add items before checking out.")
                    else:
                        st.session_state.delivery_method = delivery_method
                        st.session_state.checkout_step = 2
                        st.rerun()

        # STEP 2: Payment Selection
        elif step == 2:
            st.markdown("#### **Step 2: Payment Method Selection**")
            st.info(f"Fulfillment Choice Selected: **{st.session_state.get('delivery_method')}**")
            
            with st.form("payment_form"):
                payment_method = st.radio("Choose your billing framework:", ["Cash on Delivery", "Debit Card", "Credit Card"])
                col_back, col_next = st.columns(2)
                
                with col_back:
                    back = st.form_submit_button("⬅️ Back")
                with col_next:
                    submit_step2 = st.form_submit_button("Proceed to Customer Info ➡️")
                
                if back:
                    st.session_state.checkout_step = 1
                    st.rerun()
                if submit_step2:
                    st.session_state.payment_method = payment_method
                    st.session_state.checkout_step = 3
                    st.rerun()

        # STEP 3: Contact & Address Data Validation Form
        elif step == 3:
            st.markdown("#### **Step 3: Contact & Delivery Address Validation**")
            st.info(f"Fulfillment: **{st.session_state.get('delivery_method')}** | Payment: **{st.session_state.get('payment_method')}**")
            
            is_delivery = st.session_state.get("delivery_method") == "Home Delivery"

            with st.form("customer_details_form"):
                name = st.text_input("Full Name *")
                phone = st.text_input("Phone Number *")
                email = st.text_input("Email Address *")
                
                # Conditional Address Box Requirement Verification
                address = ""
                if is_delivery:
                    address = st.text_area("Full Shipping Address *")
                else:
                    st.warning("🏪 Store Pick-up address: 45-Commercial Zone, Jerry Shoes Center, PK.")
                    address = "Store Pickup Location Selected"

                col_back2, col_confirm = st.columns(2)
                with col_back2:
                    back2 = st.form_submit_button("⬅️ Back")
                with col_confirm:
                    confirm_order = st.form_submit_button("🎯 Confirm & Place Order")

                if back2:
                    st.session_state.checkout_step = 2
                    st.rerun()

                if confirm_order:
                    # Comprehensive Data Form Validations Block
                    if not name.strip() or not phone.strip() or not email.strip() or (is_delivery and not address.strip()):
                        st.error("🚨 Validation Failed: Please fill all required fields marked with * before continuing.")
                    elif not st.session_state.cart:
                        st.error("🚨 Error: Your cart was modified and is empty. System halted.")
                    else:
                        # Process Order Generation
                        order_id = str(uuid.uuid4())[:8].upper()
                        customer_info = {"name": name, "phone": phone, "email": email, "address": address}
                        
                        with st.spinner("Processing transaction and alerting dispatch..."):
                            email_sent = send_order_email(
                                order_id, 
                                st.session_state.cart, 
                                total_amount, 
                                st.session_state.delivery_method, 
                                st.session_state.payment_method, 
                                customer_info
                            )
                        
                        # Show receipt display
                        st.balloons()
                        st.success(f"📦 Order Successfully Placed! Reference Code: **#{order_id}**")
                        
                        with st.container(border=True):
                            st.markdown(f"### **Invoice Summary [#{order_id}]**")
                            st.write(f"**Customer:** {name} | **Method:** {st.session_state.delivery_method}")
                            st.write(f"**Total Amount Transacted:** Rs. {total_amount:,}")
                            if email_sent:
                                st.caption("📩 System Dispatch Note: A detailed manifest breakdown email has been beamed directly to the store owners.")
                            else:
                                st.caption("⚠️ Notification Dispatch Exception: Order stored natively, dispatch notification system pending.")
                        
                        # Clear configuration arrays to allow clean subsequent ordering loops
                        st.session_state.cart = []
                        st.session_state.checkout_step = 1
                        # Prevent immediate re-execution lockups
                        st.stop()

# ==========================================
# PAGE 3: CONTACT US / FOOTER LAYOUT
# ==========================================
elif page == "Contact Us":
    st.title("📞 Contact Jerry Shoes Outlet")
    st.markdown("---")
    
    st.subheader("📍 Corporate Headquarters")
    st.markdown("""
    **Jerry Shoes Outlet Ltd.** 45-Commercial Zone, Block C,  
    Phase 5, DHA, Lahore, Pakistan.  
    
    * **Customer Support Hotline:** +92 (42) 111-537-797  
    * **Official Operations Mailbox:** support@jerryshoesoutlet.com  
    """)
    
    st.markdown("---")
    st.subheader("🌐 Social Ecosystem Links")
    st.write("Join our communities across networks for product drops and announcements:")
    
    col_insta, col_linked = st.columns(2)
    with col_insta:
        st.link_button("📸 Follow Us on Instagram", "https://instagram.com/jerryshoesoutlet_placeholder")
    with col_linked:
        st.link_button("💼 Connect with Us on LinkedIn", "https://linkedin.com/company/jerryshoesoutlet_placeholder")

# ==========================================
# PAGE 4: HIDDEN ADMIN PANEL LOGIC
# ==========================================
elif page == "Admin Panel Auth":
    if not is_admin_authenticated:
        st.title("🔒 Admin Control Matrix Locked")
        st.warning("Please supply administrative passwords inside the security box localized inside the sidebar.")
    else:
        st.title("🛠️ Store Operations Dashboard")
        st.write("Manage pricing indices, update product descriptions, and switch asset availability metrics.")
        
        tab_add, tab_edit = st.tabs(["🆕 Provision New Shoe Item", "✏️ Edit Existing Catalog Matrix"])
        
        # TAB 1: ADD NEW ENTRY
        with tab_add:
            with st.form("add_new_product_form"):
                new_name = st.text_input("Shoe Model Name")
                new_brand = st.text_input("Brand Classification Label")
                new_price = st.number_input("Retail Price Assessment (PKR)", min_value=0, step=500, value=15000)
                new_img = st.text_input("Image Asset Endpoint URL", value="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500")
                new_avail = st.checkbox("Enable For Distribution Instantly", value=True)
                
                submit_new = st.form_submit_button("Deploy to Production Catalog")
                
                if submit_new:
                    if not new_name.strip() or not new_brand.strip():
                        st.error("Validation Halt: Product Designation and Brand categorization labels cannot be left blank.")
                    else:
                        generated_id = str(len(st.session_state.products) + 1)
                        st.session_state.products.append({
                            "id": generated_id,
                            "name": new_name,
                            "brand": new_brand,
                            "price": int(new_price),
                            "image": new_img,
                            "available": new_avail
                        })
                        st.success(f"Successfully integrated '{new_name}' into dynamic store inventory.")
                        st.rerun()

        # TAB 2: UPDATE MANIFEST RECORDS
        with tab_edit:
            st.markdown("### Alter Operational Attributes")
            for idx, prod in enumerate(st.session_state.products):
                with st.expander(f"📦 ID {prod['id']}: {prod['name']} ({prod['brand']})"):
                    # Use unique keys utilizing the immutable unique index structures
                    updated_name = st.text_input("Model Name", value=prod['name'], key=f"edit_name_{prod['id']}")
                    updated_brand = st.text_input("Brand Title", value=prod['brand'], key=f"edit_brand_{prod['id']}")
                    updated_price = st.number_input("Price Matrix Index Point (PKR)", value=int(prod['price']), step=500, key=f"edit_price_{prod['id']}")
                    updated_avail = st.checkbox("Global Inventory Availability Token", value=prod['available'], key=f"edit_avail_{prod['id']}")
                    
                    if st.button("Commit Asset Manifest Modifications", key=f"commit_btn_{prod['id']}"):
                        st.session_state.products[idx]['name'] = updated_name
                        st.session_state.products[idx]['brand'] = updated_brand
                        st.session_state.products[idx]['price'] = int(updated_price)
                        st.session_state.products[idx]['available'] = updated_avail
                        st.success("Successfully modified item state metrics!")
                        st.rerun()

# ==========================================
# GLOBAL STATIC STRUCTURAL FOOTER
# ==========================================
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© 2026 Jerry Shoes Outlet Inc. All rights reserved.</p>", unsafe_allow_html=True)
