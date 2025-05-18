import flet as ft
from typing import Callable

def create_login_view(handle_login: Callable[[str, str], None]) -> ft.Container:
    """
    Create login view with username and password fields.
    
    Args:
        handle_login: Callback function for login
        
    Returns:
        Container with login form
    """
    # Create form fields
    username_field = ft.TextField(
        label="Username",
        border=ft.InputBorder.OUTLINE,
        prefix_icon=ft.icons.PERSON,
        width=400,
        autofocus=True
    )
    
    password_field = ft.TextField(
        label="Password",
        border=ft.InputBorder.OUTLINE,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK,
        width=400
    )
    
    # Create login button
    login_button = ft.ElevatedButton(
        text="Login",
        icon=ft.icons.LOGIN,
        on_click=lambda _: handle_login(username_field.value, password_field.value),
        width=400
    )
    
    # Create register button
    register_button = ft.TextButton(
        text="Create an account",
        on_click=lambda _: ft.page.go("/register"),
        width=400
    )
    
    # Create form
    form = ft.Column(
        [
            ft.Text("Nissan EV Battery Predictor", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Sign in to your account", size=16, color=ft.colors.GREY_700),
            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            username_field,
            password_field,
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            login_button,
            register_button
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    # Create card container
    card = ft.Card(
        content=ft.Container(
            content=form,
            padding=30,
            width=500
        ),
        elevation=5
    )
    
    # Add Nissan logo at the top
    logo = ft.Column(
        [
            ft.Icon(ft.icons.ELECTRIC_CAR, size=80, color=ft.colors.BLUE),
            ft.Text("NISSAN", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    
    # Create container
    container = ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Divider(height=40, color=ft.colors.TRANSPARENT),
                card
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        padding=50
    )
    
    return container

def create_register_view(handle_register: Callable[[str, str, str], None]) -> ft.Container:
    """
    Create registration view with form fields.
    
    Args:
        handle_register: Callback function for registration
        
    Returns:
        Container with registration form
    """
    # Create form fields
    username_field = ft.TextField(
        label="Username",
        border=ft.InputBorder.OUTLINE,
        prefix_icon=ft.icons.PERSON,
        width=400,
        autofocus=True,
        helper_text="Username must be at least 3 characters"
    )
    
    password_field = ft.TextField(
        label="Password",
        border=ft.InputBorder.OUTLINE,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK,
        width=400,
        helper_text="Password must be at least 8 characters with at least one digit and one uppercase letter"
    )
    
    confirm_password_field = ft.TextField(
        label="Confirm Password",
        border=ft.InputBorder.OUTLINE,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK,
        width=400,
        helper_text="Passwords must match"
    )
    
    # Create register button
    register_button = ft.ElevatedButton(
        text="Register",
        icon=ft.icons.PERSON_ADD,
        on_click=lambda _: handle_register(
            username_field.value,
            password_field.value,
            confirm_password_field.value
        ),
        width=400
    )
    
    # Create back button
    back_button = ft.TextButton(
        text="Back to login",
        on_click=lambda _: ft.page.go("/"),
        width=400
    )
    
    # Create form
    form = ft.Column(
        [
            ft.Text("Create an Account", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Sign up for Nissan EV Battery Predictor", size=16, color=ft.colors.GREY_700),
            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            username_field,
            password_field,
            confirm_password_field,
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            register_button,
            back_button
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    # Create card container
    card = ft.Card(
        content=ft.Container(
            content=form,
            padding=30,
            width=500
        ),
        elevation=5
    )
    
    # Add Nissan logo at the top
    logo = ft.Column(
        [
            ft.Icon(ft.icons.ELECTRIC_CAR, size=80, color=ft.colors.BLUE),
            ft.Text("NISSAN", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    
    # Create container
    container = ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Divider(height=40, color=ft.colors.TRANSPARENT),
                card
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        padding=50
    )
    
    return container