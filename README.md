# ThreadLine: Fashion E-Commerce

A full-stack Django fashion store.

## Team

- M A Zunaid Arbaaz: Forms, views: product_upload, product_edit
- Naga Sai Bharath Potla: Store Templates & Bootstrap UI; views: order history, about
- Ajay Kasturi: Database: models, database seeding; views: product_details, product_delete
- John Rahul Vijay Raj: Views: add review, get_cart, add_to_cart, cart_view, remove_from_cart, check_out, ProductListView
- Mohammed Farhan Anwar: templates: registration; views: register, profile, contact

## Features

| item                                          | Where                                                           |
| --------------------------------------------- | --------------------------------------------------------------- |
| Authentication (login/logout/forgot password) | Django built-in auth + `templates/registration/`                |
| Forms, Models, CRUD                           | `store/forms.py`, `store/models.py`, product upload/edit/delete |
| User Sessions & Cookies (history)             | session cart + recently-viewed in `store/views.py`              |
| Search + Dropdown Filter                      | `ProductListView` in `store/views.py`, `index.html`             |
| File Upload                                   | product image + profile avatar (`ImageField`)                   |
| Registered vs Guest                           | `@login_required` on checkout, reviews, upload                  |
| Bootstrap UI                                  | `static/css/style.css` + Bootstrap 5                            |
                                   

## Setup (PyCharm or terminal)

```bash
python -m venv venv
# Windows: venv\Scripts\activate   |   Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser # for admin access
python manage.py runserver
```

Open http://127.0.0.1:8000

## Demo login

- User: `demo` Password: `demo12345`
- Admin: create with `createsuperuser`

## Forgot password

By default the reset link prints in the terminal (console email, always works for demos).
To send real emails, see the commented Gmail SMTP block in `threadline/settings.py`.

## Run tests

```bash
python manage.py test
```
