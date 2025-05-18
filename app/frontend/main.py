import flet as ft
import httpx
import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Callable, Tuple
import time

# Import components
from components.auth import create_login_view, create_register_view
from components.dashboard import create_dashboard_view
from components.file_management import create_file_management_view
from components.model_training import create_model_training_view
from components.visualization import create_visualization_view
from services import ApiService

# Configure API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

def main(page: ft.Page):
    """Main entry point for Flet application."""
    # Set page properties
    page.title = "Nissan EV Battery Predictor"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 1200
    page.window_height = 800
    
    # Initialize API service
    api_service = ApiService(API_URL)
    
    # Application state
    app_state = {
        "token": None,
        "user": None,
        "current_view": "/",
        "current_file_id": None,
        "current_task_id": None,
        "files": [],
        "models": [],
        "current_model": None,
    }
    
    # Auth event handlers
    async def handle_login(username: str, password: str):
        """Handle login form submission."""
        try:
            result = await api_service.login(username, password)
            if result["success"]:
                app_state["token"] = result["access_token"]
                api_service.set_token(result["access_token"])
                app_state["user"] = {"username": username}
                
                # Show success message
                page.snack_bar = ft.SnackBar(content=ft.Text("Login successful"))
                page.snack_bar.open = True
                
                # Navigate to dashboard
                page.go("/dashboard")
            else:
                # Show error message
                page.snack_bar = ft.SnackBar(content=ft.Text(result["message"]))
                page.snack_bar.open = True
            
            page.update()
        except Exception as e:
            # Show error message
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(e)}"))
            page.snack_bar.open = True
            page.update()
    
    async def handle_register(username: str, password: str, confirm_password: str):
        """Handle user registration form submission."""
        if password != confirm_password:
            page.snack_bar = ft.SnackBar(content=ft.Text("Passwords do not match"))
            page.snack_bar.open = True
            page.update()
            return
        
        try:
            result = await api_service.register(username, password)
            if result["success"]:
                # Show success message
                page.snack_bar = ft.SnackBar(content=ft.Text("Registration successful"))
                page.snack_bar.open = True
                page.update()
                
                # Navigate to login
                page.go("/")
            else:
                # Show error message
                page.snack_bar = ft.SnackBar(content=ft.Text(result["message"]))
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            # Show error message
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(e)}"))
            page.snack_bar.open = True
            page.update()
    
    # File management event handlers
    async def handle_upload_file(e: ft.FilePickerResultEvent):
        """Handle file upload."""
        if not e.files:
            return
        
        try:
            upload_file = e.files[0]
            
            # Check file type
            if not upload_file.name.endswith(".csv"):
                page.snack_bar = ft.SnackBar(content=ft.Text("Only CSV files are supported"))
                page.snack_bar.open = True
                page.update()
                return
            
            # Upload file
            result = await api_service.upload_file(upload_file)
            
            if result["success"]:
                # Refresh file list
                await refresh_files()
                
                # Show success message
                page.snack_bar = ft.SnackBar(content=ft.Text("File uploaded successfully"))
                page.snack_bar.open = True
                page.update()
            else:
                # Show error message
                page.snack_bar = ft.SnackBar(content=ft.Text(result["message"]))
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            # Show error message
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error uploading file: {str(e)}"))
            page.snack_bar.open = True
            page.update()
    
    async def handle_delete_file(file_id: int):
        """Handle file deletion."""
        try:
            result = await api_service.delete_file(file_id)
            
            if result["success"]:
                # Refresh file list
                await refresh_files()
                
                # Show success message
                page.snack_bar = ft.SnackBar(content=ft.Text("File deleted successfully"))
                page.snack_bar.open = True
                page.update()
            else:
                # Show error message
                page.snack_bar = ft.SnackBar(content=ft.Text(result["message"]))
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            # Show error message
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error deleting file: {str(e)}"))
            page.snack_bar.open = True
            page.update()
    
    async def handle_preprocess_file(file_id: int):
        """Handle file preprocessing."""
        try:
            # Show loading indicator
            page.splash = ft.ProgressBar()
            page.update()
            
            # Preprocess file
            result = await api_service.preprocess_file(file_id)
            
            if result["success"]:
                app_state["current_task_id"] = result["task_id"]
                
                # Poll task status
                await poll_task_status(result["task_id"], "Preprocessing file...")
                
                # Refresh file list
                await refresh_files()
                
                # Hide loading indicator
                page.splash = None
                page.update()
            else:
                # Hide loading indicator
                page.splash = None
                
                # Show error message
                page.snack_bar = ft.SnackBar(content=ft.Text(result["message"]))
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            # Hide loading indicator
            page.splash = None
            
            # Show error message
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error preprocessing file: {str(e)}"))
            page.snack_bar.open = True
            page.update()
    
    # Model training event handlers
    async def handle_train_model(file_id: int, model_type: str, params: Dict[str, Any], polynomial_degree: int = 1):
        """Handle model training."""
        try:
            # Show loading indicator
            page.splash = ft.ProgressBar()
            page.update()
            
            # Train model
            result = await api_service.train_model(file_id, model_type, params, polynomial_degree)
            
            if result["success"]:
                app_state["current_task_id"] = result["task_id"]
                
                # Poll task status
                model_result = await poll_task_status(result["task_id"], "Training model...")
                
                if model_result and "visualization_data" in model_result:
                    # Store model result
                    app_state["current_model"] = model_result
                    
                    # Navigate to visualization view
                    page.go("/visualization")
                
                # Hide loading indicator
                page.splash = None
                page.update()
            else:
                # Hide loading indicator
                page.splash = None
                
                # Show error message
                page.snack_bar = ft.SnackBar(content=ft.Text(result["message"]))
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            # Hide loading indicator
            page.splash = None
            
            # Show error message
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error training model: {str(e)}"))
            page.snack_bar.open = True
            page.update()
    
    # Helper functions
    async def refresh_files():
        """Refresh file list."""
        try:
            result = await api_service.list_files()
            
            if result["success"]:
                app_state["files"] = result["files"]
                page.update()
        except Exception as e:
            print(f"Error refreshing files: {str(e)}")
    
    async def refresh_models():
        """Refresh model list."""
        try:
            result = await api_service.list_models()
            
            if result["success"]:
                app_state["models"] = result["models"]
                page.update()
        except Exception as e:
            print(f"Error refreshing models: {str(e)}")
    
    async def poll_task_status(task_id: str, message: str) -> Optional[Dict[str, Any]]:
        """
        Poll Celery task status until completion.
        
        Args:
            task_id: Celery task ID
            message: Message to display during polling
            
        Returns:
            Task result or None if task failed
        """
        # Create progress dialog
        progress_text = ft.Text(message)
        progress_bar = ft.ProgressBar(width=400)
        
        progress_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Processing"),
            content=ft.Column([
                progress_text,
                progress_bar,
            ], tight=True),
        )
        
        # Show progress dialog
        page.dialog = progress_dialog
        progress_dialog.open = True
        page.update()
        
        # Poll task status
        while True:
            try:
                # Get task status
                result = await api_service.get_task_status(task_id)
                
                # Update progress text
                if "state" in result:
                    progress_text.value = f"{message} ({result['state']})"
                    page.update()
                
                # Check if task completed
                if result.get("state") == "SUCCESS":
                    # Close progress dialog
                    progress_dialog.open = False
                    page.update()
                    
                    # Show success message
                    page.snack_bar = ft.SnackBar(content=ft.Text("Task completed successfully"))
                    page.snack_bar.open = True
                    page.update()
                    
                    # Return task result
                    return result.get("result")
                
                # Check if task failed
                elif result.get("state") == "FAILURE":
                    # Close progress dialog
                    progress_dialog.open = False
                    page.update()
                    
                    # Show error message
                    error_message = result.get("status", "Task failed")
                    page.snack_bar = ft.SnackBar(content=ft.Text(error_message))
                    page.snack_bar.open = True
                    page.update()
                    
                    return None
                
                # Wait before polling again
                await asyncio.sleep(1)
            
            except Exception as e:
                # Close progress dialog
                progress_dialog.open = False
                page.update()
                
                # Show error message
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Error polling task status: {str(e)}"))
                page.snack_bar.open = True
                page.update()
                
                return None
    
    # Create file picker
    file_picker = ft.FilePicker(on_result=handle_upload_file)
    page.overlay.append(file_picker)
    
    # Navigation functions
    def handle_sign_out():
        """Handle sign out."""
        app_state["token"] = None
        app_state["user"] = None
        api_service.clear_token()
        
        # Navigate to login
        page.go("/")
    
    # Route configuration
    def route_change(route):
        """Handle route changes and update the UI accordingly."""
        app_state["current_view"] = route.route
        page.views.clear()
        
        # Check auth for protected routes
        if route.route.startswith("/dashboard") or route.route.startswith("/files") or \
           route.route.startswith("/train") or route.route.startswith("/visualization"):
            if not app_state["token"]:
                # Redirect to login
                page.go("/")
                return
        
        # Handle routes
        if route.route == "/" or route.route == "/login":
            # Login view
            page.views.append(
                ft.View(
                    "/",
                    [create_login_view(handle_login)],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    padding=50
                )
            )
        
        elif route.route == "/register":
            # Register view
            page.views.append(
                ft.View(
                    "/register",
                    [create_register_view(handle_register)],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    padding=50
                )
            )
        
        elif route.route == "/dashboard":
            # Dashboard view
            page.views.append(
                ft.View(
                    "/dashboard",
                    [create_dashboard_view(
                        app_state["user"]["username"], 
                        handle_sign_out,
                        lambda: page.go("/files"),
                        lambda: page.go("/models"),
                    )],
                    padding=20
                )
            )
            
            # Refresh data
            asyncio.create_task(refresh_files())
            asyncio.create_task(refresh_models())
        
        elif route.route == "/files":
            # File management view
            page.views.append(
                ft.View(
                    "/files",
                    [create_file_management_view(
                        app_state["files"],
                        lambda: file_picker.pick_files(allow_multiple=False),
                        handle_delete_file,
                        handle_preprocess_file,
                        lambda file_id: page.go(f"/train/{file_id}"),
                        lambda: page.go("/dashboard"),
                    )],
                    padding=20
                )
            )
            
            # Refresh files
            asyncio.create_task(refresh_files())
        
        elif route.route.startswith("/train/"):
            # Extract file ID from route
            file_id = int(route.route.split("/")[-1])
            app_state["current_file_id"] = file_id
            
            # Find file in state
            file = next((f for f in app_state["files"] if f["id"] == file_id), None)
            
            if not file:
                # File not found, redirect to files
                page.go("/files")
                return
            
            # Model training view
            page.views.append(
                ft.View(
                    f"/train/{file_id}",
                    [create_model_training_view(
                        file,
                        lambda model_type, params, polynomial_degree: 
                            handle_train_model(file_id, model_type, params, polynomial_degree),
                        lambda: page.go("/files"),
                    )],
                    padding=20
                )
            )
        
        elif route.route == "/visualization" and app_state["current_model"]:
            # Visualization view
            page.views.append(
                ft.View(
                    "/visualization",
                    [create_visualization_view(
                        app_state["current_model"],
                        lambda: page.go("/dashboard"),
                    )],
                    padding=20
                )
            )
        
        else:
            # Default to login view
            page.go("/")
            return
        
        page.update()
    
    # Configure page routes
    page.on_route_change = route_change
    page.go(page.route)

# Run the app
ft.app(target=main)