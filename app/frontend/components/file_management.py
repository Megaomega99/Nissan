import flet as ft
from typing import Callable, List, Dict, Any

def create_file_management_view(
    files: List[Dict[str, Any]],
    handle_upload: Callable[[], None],
    handle_delete: Callable[[int], None],
    handle_preprocess: Callable[[int], None],
    navigate_to_train: Callable[[int], None],
    navigate_to_dashboard: Callable[[], None]
) -> ft.Container:
    """
    Create file management view with file list and actions.
    
    Args:
        files: List of file data
        handle_upload: Callback function for file upload
        handle_delete: Callback function for file deletion
        handle_preprocess: Callback function for file preprocessing
        navigate_to_train: Callback function to navigate to training view
        navigate_to_dashboard: Callback function to navigate to dashboard
        
    Returns:
        Container with file management UI
    """
    # Create app bar
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            on_click=lambda _: navigate_to_dashboard()
        ),
        leading_width=40,
        title=ft.Text("Manage Files"),
        center_title=False,
        bgcolor=ft.colors.BLUE
    )
    
    # Create upload button
    upload_button = ft.ElevatedButton(
        text="Upload CSV",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: handle_upload()
    )
    
    # Create file list
    file_list = ft.ListView(
        spacing=10,
        padding=10,
        auto_scroll=True
    )
    
    # Helper function to create file card
    def create_file_card(file: Dict[str, Any]) -> ft.Card:
        """Create a card for a file with actions."""
        # Format upload date
        upload_date = file.get("upload_date", "").split("T")[0]
        
        # Create status chip based on file status
        status = file.get("status", "uploaded")
        status_color = {
            "uploaded": ft.colors.BLUE,
            "preprocessing": ft.colors.ORANGE,
            "preprocessed": ft.colors.GREEN,
            "training": ft.colors.PURPLE,
            "processed": ft.colors.TEAL
        }.get(status, ft.colors.GREY)
        
        status_chip = ft.Chip(
            label=status.capitalize(),
            bgcolor=status_color,
            label_style=ft.TextStyle(color=ft.colors.WHITE)
        )
        
        # Create file size text
        file_size_text = ""
        if file.get("file_size"):
            size_kb = file["file_size"] / 1024
            if size_kb < 1024:
                file_size_text = f"{size_kb:.1f} KB"
            else:
                file_size_text = f"{size_kb/1024:.1f} MB"
        
        # Create action buttons based on file status
        action_buttons = []
        
        # Preprocess button
        if status == "uploaded":
            action_buttons.append(
                ft.IconButton(
                    icon=ft.icons.AUTO_FIX_HIGH,
                    tooltip="Preprocess",
                    on_click=lambda _: handle_preprocess(file["id"])
                )
            )
        
        # Train button
        if status == "preprocessed" or status == "processed":
            action_buttons.append(
                ft.IconButton(
                    icon=ft.icons.MODEL_TRAINING,
                    tooltip="Train Model",
                    on_click=lambda _: navigate_to_train(file["id"])
                )
            )
        
        # Delete button (always available)
        action_buttons.append(
            ft.IconButton(
                icon=ft.icons.DELETE,
                tooltip="Delete",
                on_click=lambda _: handle_delete(file["id"])
            )
        )
        
        # Create file card
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.INSERT_DRIVE_FILE, size=30, color=ft.colors.BLUE),
                        ft.Column(
                            [
                                ft.Text(file["filename"], weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    [
                                        ft.Text(f"Uploaded: {upload_date}", size=12),
                                        ft.Text(f"Size: {file_size_text}", size=12) if file_size_text else ft.Container(),
                                    ],
                                    spacing=10
                                )
                            ],
                            spacing=5,
                            expand=True
                        ),
                        status_chip,
                        ft.Row(action_buttons, spacing=0)
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=15
            )
        )
    
    # Add files to list
    for file in files:
        file_list.controls.append(create_file_card(file))
    
    # Create empty state if no files
    if not files:
        file_list.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.icons.NO_SIM, size=50, color=ft.colors.GREY_400),
                        ft.Text("No files uploaded yet", size=16, color=ft.colors.GREY_400),
                        ft.Text("Upload a CSV file to get started", size=14, color=ft.colors.GREY_400)
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center,
                height=200
            )
        )
    
    # Create instructions card
    instructions_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.INFO, size=24, color=ft.colors.BLUE),
                            ft.Text("File Management Instructions", weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Text(
                        "1. Upload a CSV file with battery data (single column of values)\n"
                        "2. Preprocess the file to remove nulls and infinite values\n"
                        "3. Train ML models on the preprocessed data\n"
                        "4. Delete files when you no longer need them"
                    )
                ],
                spacing=10
            ),
            padding=20
        )
    )
    
    # Create main content
    content = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("File Management", size=24, weight=ft.FontWeight.BOLD),
                    upload_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            instructions_card,
            ft.Divider(),
            ft.Text("Your Files", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=file_list,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10,
                padding=10,
                expand=True
            )
        ],
        spacing=20,
        expand=True
    )
    
    # Create main container
    container = ft.Container(
        content=ft.Column(
            [
                app_bar,
                ft.Container(
                    content=content,
                    padding=20,
                    expand=True
                )
            ],
            spacing=0,
            expand=True
        ),
        padding=0,
        expand=True
    )
    
    return container