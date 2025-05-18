import flet as ft
from typing import Callable

def create_dashboard_view(
    username: str,
    handle_sign_out: Callable[[], None],
    navigate_to_files: Callable[[], None],
    navigate_to_models: Callable[[], None]
) -> ft.Container:
    """
    Create dashboard view with app navigation options.
    
    Args:
        username: Current user's username
        handle_sign_out: Callback function for sign out
        navigate_to_files: Callback function to navigate to files view
        navigate_to_models: Callback function to navigate to models view
        
    Returns:
        Container with dashboard UI
    """
    # Create app bar
    app_bar = ft.AppBar(
        leading=ft.Icon(ft.icons.ELECTRIC_CAR),
        leading_width=40,
        title=ft.Text("Nissan EV Battery Predictor"),
        center_title=False,
        bgcolor=ft.colors.BLUE,
        actions=[
            ft.IconButton(
                icon=ft.icons.LOGOUT,
                icon_color=ft.colors.WHITE,
                tooltip="Sign out",
                on_click=lambda _: handle_sign_out()
            )
        ]
    )
    
    # Create welcome card
    welcome_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.PERSON, size=30, color=ft.colors.BLUE),
                            ft.Text(f"Welcome, {username}", size=20, weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10
                    ),
                    ft.Text(
                        "Use this application to upload CSV files, preprocess data, "
                        "train ML models, and visualize predictions for EV battery states.",
                        size=16
                    )
                ],
                spacing=10
            ),
            width=800,
            padding=20
        )
    )
    
    # Create action cards
    files_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.UPLOAD_FILE, size=24, color=ft.colors.BLUE),
                            ft.Text("Manage Files", weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Text("Upload, delete, and preprocess CSV files for analysis."),
                    ft.ElevatedButton(
                        text="Go to Files",
                        icon=ft.icons.ARROW_FORWARD,
                        on_click=lambda _: navigate_to_files()
                    )
                ],
                spacing=10
            ),
            width=350,
            height=200,
            padding=20
        ),
        elevation=5
    )
    
    models_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.MODEL_TRAINING, size=24, color=ft.colors.BLUE),
                            ft.Text("Train Models", weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Text("Train ML models to predict EV battery states."),
                    ft.ElevatedButton(
                        text="Go to Models",
                        icon=ft.icons.ARROW_FORWARD,
                        on_click=lambda _: navigate_to_models()
                    )
                ],
                spacing=10
            ),
            width=350,
            height=200,
            padding=20
        ),
        elevation=5
    )
    
    # Create info card
    info_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.INFO, size=24, color=ft.colors.BLUE),
                            ft.Text("About the Application", weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Text(
                        "This application helps analyze and predict the state of "
                        "electric vehicle batteries based on historical data. "
                        "Upload your CSV data, train different ML models, and get predictions."
                    ),
                    ft.Row(
                        [
                            ft.Text("Technologies used:"),
                            ft.Chip(label="FastAPI", leading=ft.Icon(ft.icons.API)),
                            ft.Chip(label="Flet", leading=ft.Icon(ft.icons.WEB)),
                            ft.Chip(label="PostgreSQL", leading=ft.Icon(ft.icons.STORAGE)),
                            ft.Chip(label="Celery", leading=ft.Icon(ft.icons.SCHEDULE)),
                            ft.Chip(label="Scikit-learn", leading=ft.Icon(ft.icons.SCIENCE)),
                        ],
                        wrap=True,
                        spacing=5
                    )
                ],
                spacing=15
            ),
            width=800,
            padding=20
        ),
        elevation=5
    )
    
    # Create dashboard layout
    content = ft.Column(
        [
            welcome_card,
            ft.Divider(),
            ft.Text("Quick Actions", size=18, weight=ft.FontWeight.BOLD),
            ft.Row(
                [files_card, models_card],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            ),
            ft.Divider(),
            info_card
        ],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    # Create main container
    container = ft.Container(
        content=ft.Column(
            [
                app_bar,
                ft.Container(
                    content=content,
                    padding=20
                )
            ],
            spacing=0
        ),
        padding=0
    )
    
    return container