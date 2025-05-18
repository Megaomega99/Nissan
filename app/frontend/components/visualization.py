import flet as ft
from typing import Callable, Dict, Any

def create_visualization_view(
    model_result: Dict[str, Any],
    navigate_back: Callable[[], None]
) -> ft.Container:
    """
    Create visualization view with model results and predictions.
    
    Args:
        model_result: Model training result data
        navigate_back: Callback function to navigate back
        
    Returns:
        Container with visualization UI
    """
    # Create app bar
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            on_click=lambda _: navigate_back()
        ),
        leading_width=40,
        title=ft.Text("Model Results"),
        center_title=False,
        bgcolor=ft.colors.BLUE
    )
    
    # Extract data from model result
    metrics = model_result.get("metrics", {})
    visualization_data = model_result.get