# Guerrier - Testing Documentation

Return back to the [README.md](README.md) file.

During the development of this project, various tests were carried out to ensure the website was functioning properly. In this section, you will find documentation on all tests performed on the site.

## Table of Contents

- [Browser Compatibility Testing](#browser-compatibility-testing)
- [Code Validation](#code-validation)
  - [HTML](#html)
  - [CSS](#css)
  - [JavaScript](#javascript)
  - [Python](#python)
- [Lighthouse Audit](#lighthouse-audit)
- [Responsiveness](#responsiveness)
- [Manual Testing](#manual-testing)
- [User Story Testing](#user-story-testing)
- [Feature Testing](#feature-testing)
- [Usability Testing](#usability-testing)

## Browser Compatibility Testing

It is important to test on different browsers to ensure that the site is functional as expected across them all.

<details>
<summary>Chrome</summary>

![Chrome Browser Testing](documentation/readme_images/chrome.png)
</details>

<details>
<summary>Safari</summary>

![Safari Browser Testing](documentation/safari.png)
</details>

<details>
<summary>Firefox</summary>

![Firefox Browser Testing](documentation/firefox.png)
</details>

[Back to Top](#table-of-contents)


## Code Validation

### HTML

[HTML W3C Validator](https://validator.w3.org) has been used to validate all HTML files.

<details>
<summary>Home</summary>

![Home Page HTML Validation](documentation/validation/html_home.png)
</details>

<details>
<summary>All Products</summary>

![All Products HTML Validation](documentation/validation/html_products.png)
</details>

<details>
<summary>Product Detail</summary>

![Product Detail HTML Validation](documentation/validation/html_product-detail.png)
</details>

<details>
<summary>Contact</summary>

![Contact HTML Validation](documentation/validation/html_contact.png)
</details>

<details>
<summary>Privacy Policy</summary>

![Privacy Policy HTML Validation](documentation/validation/html_privacy_policy.png)
</details>

<details>
<summary>Returns</summary>

![Returns HTML Validation](documentation/validation/html_returns.png)
</details>

<details>
<summary>Sign Up</summary>

![Sign Up HTML Validation](documentation/validation/html_signup.png)
</details>

<details>
<summary>Sign In</summary>

![Sign In HTML Validation](documentation/validation/html_signin.png)
</details>

<details>
<summary>Search</summary>

![Search HTML Validation](documentation/validation/html_search.png)
</details>

<details>
<summary>Log Out</summary>

![Log Out HTML Validation](documentation/validation/html_logout.png)
</details>

<details>
<summary>Shopping Bag</summary>

![Shopping Bag HTML Validation](documentation/validation/html_bag.png)
</details>

<details>
<summary>Checkout</summary>

![Checkout HTML Validation](documentation/validation/html_checkout.png)
</details>

<details>
<summary>Checkout Success</summary>

![Checkout Success HTML Validation](documentation/validation/html_checkout_success.png)
</details>

<details>
<summary>Profile</summary>

![Profile HTML Validation](documentation/validation/html_profiles.png)
</details>

<details>
<summary>Add Product</summary>

![Add Product HTML Validation](documentation/validation/html_add_product.png)
</details>

<details>
<summary>Edit Product</summary>

![Edit Product HTML Validation](documentation/validation/html_edit_product.png)
</details>

<details>
<summary>Update Review</summary>

![Update Review HTML Validation](documentation/validation/html_update_review.png)
</details> 

<details>
<summary>Delete Review</summary>

![Delete Review HTML Validation](documentation/validation/html_delete_review.png)
</details>

<details>
<summary>Wishlist</summary>

![Wishlist HTML Validation](documentation/validation/html_wishlist.png)
</details>

[Back to Top](#table-of-contents)

### CSS

[CSS Jigsaw Validator](https://jigsaw.w3.org/css-validator) has been used to validate all CSS files.

<details>
<summary>base.css</summary>

![Base CSS Validation](documentation/validation/css_base.png)
</details>

<details>
<summary>checkout.css</summary>

![Checkout CSS Validation](documentation/validation/css_checkout.png)
</details>

[Back to Top](#table-of-contents)

### JavaScript

[JShint Validator](https://jshint.com) has been used to validate all JS files.

<details>
<summary>scripts.js</summary>

![Scripts Validation](documentation/validation/js_scripts.png)
</details>
<summary>stripe_elements.js</summary>

![Stripe Element JS Validation](documentation/validation/js_stripe_element.png)
</details>

[Back to Top](#table-of-contents)

### Python 

[CI Python Linter](https://pep8ci.herokuapp.com) has been used to validate all Python files.

<details>
<summary>Bag contexts.py</summary>

![Bag Contexts Python Validation](documentation/validation/python-bag-contexts.png)
</details>

<details>
<summary>Bag urls.py</summary>

![Bag URLs Python Validation](documentation/validation/python-bag-urls.png)
</details>

<details>
<summary>Bag views.py</summary>

![Bag Views Python Validation](documentation/validation/python-bag-views.png)
</details>

<details>
<summary>Guerrier urls.py</summary>

![Main URLs Python Validation](documentation/validation/python-base-urls.png)
</details>

<details>
<summary>Guerrier views.py</summary>

![Main Views Python Validation](documentation/validation/python-base-views.png)
</details>

<details>
<summary>Guerrier settings.py</summary>

![Main Settings Python Validation](documentation/validation/python-base-settings.png)
</details>

<details>
<summary>Checkout admin.py</summary>

![Checkout Admin Python Validation](documentation/validation/python-checkout-admin.png)
</details>

<details>
<summary>Checkout forms.py</summary>

![Checkout Forms Python Validation](documentation/validation/python-checkout-admin.png)
</details>

<details>
<summary>Checkout models.py</summary>

![Checkout Models Python Validation](documentation/validation/python-checkout-models.png)
</details>

<details>
<summary>Checkout signals.py</summary>

![Checkout Signals Python Validation](documentation/validation/python-checkout-signal.png)
</details>

<details>
<summary>Checkout urls.py</summary>

![Checkout URLs Python Validation](documentation/validation/python-checkout-urls.png)
</details>

<details>
<summary>Checkout views.py</summary>

![Checkout Views Python Validation](documentation/validation/python-checkout-views.png)
</details>

<details>
<summary>Checkout webhook_handler.py</summary>

![Checkout Webhook Handler Python Validation](documentation/validation/python-checkout-handler.png)
</details>

<details>
<summary>Checkout webhooks.py</summary>

![Checkout Webhooks Python Validation](documentation/validation/python-checkout-webhook.png)
</details>

<details>
<summary>Home urls.py</summary>

![Home URLs Python Validation](documentation/validation/python-home-urls.png)
</details>

<details>
<summary>Home views.py</summary>

![Home Views Python Validation](documentation/validation/python-home-views.png)
</details>

<details>
<summary>Home forms.py</summary>

![Home Forms Python Validation](documentation/validation/python-home-forms.png)
</details>

<details>
<summary>Home models.py</summary>

![Home Models Python Validation](documentation/validation/python-home-models.png)
</details>

<details>
<summary>Home admin.py</summary>

![Home Admin Python Validation](documentation/validation/python-home-admin.png)
</details>

<details>
<summary>Products admin.py</summary>

![Products Admin Python Validation](documentation/validation/python-product-admin.png)
</details>

<details>
<summary>Products forms.py</summary>

![Products Forms Python Validation](documentation/validation/python-product-forms.png)
</details>

<details>
<summary>Products models.py</summary>

![Products Models Python Validation](documentation/validation/python-product-models.png)
</details>

<details>
<summary>Products urls.py</summary>

![Products URLs Python Validation](documentation/validation/python-product-urls.png)
</details>

<details>
<summary>Products views.py</summary>

![Products Views Python Validation](documentation/validation/python-product-views.png)
</details>

<details>
<summary>Products widgets.py</summary>

![Products Widgets Python Validation](documentation/validation/python-products-widgets.png)
</details>

<details>
<summary>Profiles forms.py</summary>

![Profiles Forms Python Validation](documentation/validation/python-profile-forms.png)
</details>

<details>
<summary>Profiles models.py</summary>

![Profiles Models Python Validation](documentation/validation/python-profiles-model.png)
</details>

<details>
<summary>Profiles urls.py</summary>

![Profiles URLs Python Validation](documentation/validation/python-profiles-urls.png)
</details>

<details>
<summary>Profiles views.py</summary>

![Profiles Views Python Validation](documentation/validation/python-profiles-views.png)
</details>

<details>
<summary>Wishlist admin.py</summary>

![Wishlist Admin Python Validation](documentation/validation/python-wishlist-admin.png)
</details>

<details>
<summary>Wishlist models.py</summary>

![Wishlist Models Python Validation](documentation/validation/python-wishlist-model.png)
</details>

<details>
<summary>Wishlist urls.py</summary>

![Wishlist URLs Python Validation](documentation/validation/python-wishlist-urls.png)
</details>

<details>
<summary>Wishlist views.py</summary>

![Wishlist Views Python Validation](documentation/validation/python-wishlist-views.png)
</details>

[Back to Top](#table-of-contents)

## Lighthouse Audit

I have tested the deployed project using Lighthouse in Chrome developer tools to check for any major site performance issues.

<details>
<summary>Home</summary>

![Home Lighthouse Audit](documentation/lighthouse/home-desktop.png)
</details>

<details>
<summary>Products</summary>

![Products Lighthouse Audit](documentation/lighthouse/products.png)
</details>

<details>
<summary>Product Detail</summary>

![Product Detail Lighthouse Audit](documentation/lighthouse/product-detail.png)
</details>

<details>
<summary>Contact</summary>

![Contact Lighthouse Audit](documentation/lighthouse/contact.png)
</details>

<details>
<summary>Wishlist</summary>

![Wishlist Lighthouse Audit](documentation/lighthouse/wishlist1.png)
</details>

<details>
<summary>Sign Up</summary>

![Sign Up Lighthouse Audit](documentation/lighthouse/signup1.png)
</details>

<details>
<summary>Sign In</summary>

![Sign In Lighthouse Audit](documentation/lighthouse/signin1.png)
</details>

<details>
<summary>Search</summary>

![Search Lighthouse Audit](documentation/lighthouse/search.png)
</details>

<details>
<summary>Log Out</summary>

![Log Out Lighthouse Audit](documentation/lighthouse/logout.png)
</details>

<details>
<summary>Shopping Bag</summary>

![Shopping Bag Lighthouse Audit](documentation/lighthouse/bag.png)
</details>

<details>
<summary>Checkout</summary>

![Checkout Lighthouse Audit](documentation/lighthouse/checkout1.png)
</details>

<details>
<summary>Checkout Success</summary>

![Checkout Success Lighthouse Audit](documentation/lighthouse/checkout-success.png)
</details>


[Back to Top](#table-of-contents)

## Responsiveness

The deployed project has been tested on different screen sizes to ensure it is responsive.

<details>
<summary>Mobile (DevTools - iPohn 14 Pro Max)</summary>

![Mobile Responsiveness 1](documentation/responsive/mobile_home.png)
- DevTools responsive home view
![Mobile Responsiveness 2](documentation/responsive/mobile_dropdown.png)
- DevTools resposnsive dropdown
![Mobile Responsiveness 3](documentation/responsive/mobile_footer.png)
- Devtool responsive footer
![Mobile Responsiveness 4](documentation/responsive/mobile_products.png)
 Devtool responsive products page
![Mobile Responsiveness 5](documentation/responsive/mobile_profile.png)
- Devtool responsive profile view
![Mobile Responsiveness 6](documentation/responsive/mobile_bag.png)
- Devtool responsive bag view

![Mobile Responsiveness 7](documentation/responsive/mobile_checkout.png)
- Devtool responsive checkout view

</details


<details>
<summary>Mobile (Manual Testing with Google Pixel 6A with Dark Mode enabled)</summary>

![Mobile Responsiveness 1](documentation/responsive/forced_dm_home.png)
 A forced Dark Mode home view  on Google Pixel
![Mobile Responsiveness 2](documentation/responsive/forced_dm_filter.png)
- A forced Dark Mode filter on Google Pixel
![Mobile Responsiveness 3](documentation/responsive/forced_dm_footer.png)
- A forced Dark Mode footer on Google Pixel
</details>


[Back to Top](#table-of-contents)


## Authentication & User Profiles

| User Story | Test Procedure | Result | Pass/Fail |
|------------|---------------|--------|-----------|
| As a user, I want to be able to register for an account | 1. Navigate to the register page <br> 2. Fill in required fields <br> 3. Verify email <br> 4. Log in with created credentials | User is able to register and log in with a new account | PASS |
| As a user, I want to log in and log out | 1. Navigate to login page <br> 2. Enter credentials <br> 3. Successfully log in <br> 4. Log out and confirm | User can log in and out successfully | PASS |
| As a user, I want to manage my profile | 1. Log in <br> 2. Navigate to profile <br> 3. Update information <br> 4. View order history and wishlist | User can update profile and view history | PASS |
| As an admin, I want to manage products | 1. Log in as admin <br> 2. Edit an existing product <br> 3. Delete a product <br> 4. Add a new product | Admin can manage products successfully | PASS |

## Shopping Experience

| User Story | Test Procedure | Result | Pass/Fail |
|------------|---------------|--------|-----------|
| As a shopper, I want to browse products | 1. Navigate to the products page <br> 2. Scroll through available products | Products display correctly | PASS |
| As a shopper, I want to view product details | 1. Click on a product <br> 2. View details, including images, price, and stock | Product details are displayed correctly | PASS |
| As a shopper, I want to search for products | 1. Use the search bar <br> 2. Enter search terms <br> 3. Verify search results | Search returns relevant products | PASS |
| As a shopper, I want to filter products by price | 1. Use price filter (e.g., €15 - €50) <br> 2. Verify only relevant products appear | Filter correctly applies price limits | PASS |
| As a shopper, I want to add items to my wishlist | 1. Click the wishlist icon on a product <br> 2. Verify product appears in wishlist | Product is successfully added to wishlist | PASS |
| As a shopper, I want to view related products | 1. Add an item to wishlist <br> 2. Navigate to wishlist page <br> 3. View suggested products | Related products appear correctly | PASS |

## Checkout & Payment

| User Story | Test Procedure | Result | Pass/Fail |
|------------|---------------|--------|-----------|
| As a shopper, I want to add items to my cart | 1. View product <br> 2. Select size <br> 3. Click "Add to Cart" <br> 4. Verify product appears in the cart | Product is added to the cart successfully | PASS |
| As a shopper, I want to adjust quantities in my cart | 1. Go to cart <br> 2. Update product quantity <br> 3. Verify update | Quantity updates correctly | PASS |
| As a shopper, I want to securely enter payment information | 1. Proceed to checkout <br> 2. Enter delivery and payment details <br> 3. Complete order | Payment is securely processed | PASS |
| As a shopper, I want to receive an order confirmation | 1. Complete order <br> 2. Verify confirmation page and email | Confirmation appears and email is received | PASS |

## Feature Testing

| Feature | Test Procedure | Expected Result | Actual Result | Pass/Fail |
|---------|---------------|-----------------|--------------|-----------|
| Navigation Bar | Click main navigation links | Redirects correctly | Works as expected | PASS |
| Category Dropdowns | Click dropdowns | Menus display correctly | Works as expected | PASS |
| Wishlist | Add and remove items | Wishlist updates correctly | Functions as expected | PASS |
| Related Products | View recommendations on wishlist or product pages | Related products appear | Works as expected | PASS |

## Admin Panel Features

| Feature | Test Procedure | Expected Result | Actual Result | Pass/Fail |
|---------|---------------|-----------------|--------------|-----------|
| Manage Orders | View and update order statuses | Order details update correctly | Works as expected | PASS |
| Manage Users | View and edit user profiles | Users can be updated | Works as expected | PASS |
| View Email Subscriptions | View newsletter sign-ups | Email list displays correctly | Works as expected | PASS |

## Manual Testing (Key Pages & Interactions)

| Page | User Action | Expected Result | Pass/Fail |
|------|------------|----------------|-----------|
| Home Page | Click logo | Redirects to homepage | PASS |
| Search | Enter search term | Returns relevant products | PASS |
| Product Page | Click a product | Redirects to product details | PASS |
| Wishlist | Click heart icon | Product added to wishlist | PASS |
| Shopping Cart | Adjust quantity | Cart updates correctly | PASS |
| Checkout | Complete order | Order is processed | PASS |

[Back to Top](#testing-documentation)
