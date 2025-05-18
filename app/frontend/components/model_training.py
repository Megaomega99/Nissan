import flet as ft
import json
from typing import Callable, Dict, Any

def create_model_training_view(
    file: Dict[str, Any],
    handle_train: Callable[[str, Dict[str, Any], int], None],
    navigate_back: Callable[[], None]
) -> ft.Container:
    """
    Create model training view with model selection and parameters.
    
    Args:
        file: File data
        handle_train: Callback function for model training
        navigate_back: Callback function to navigate back
        
    Returns:
        Container with model training UI
    """
    # Create app bar
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            on_click=lambda _: navigate_back()
        ),
        leading_width=40,
        title=ft.Text("Train Model"),
        center_title=False,
        bgcolor=ft.colors.BLUE
    )
    
    # Model selection dropdown
    model_dropdown = ft.Dropdown(
        label="Select Model Type",
        hint_text="Choose a model type",
        options=[
            ft.dropdown.Option("LinearRegression", text="Linear Regression"),
            ft.dropdown.Option("SVR", text="Support Vector Regression (SVR)"),
            ft.dropdown.Option("ElasticNet", text="ElasticNet Regression"),
            ft.dropdown.Option("SGD", text="Stochastic Gradient Descent (SGD)")
        ],
        autofocus=True
    )
    
    # Polynomial degree slider (for Linear Regression)
    poly_degree_slider = ft.Slider(
        min=1,
        max=5,
        divisions=4,
        label="Polynomial Degree: {value}",
        value=1,
        on_change=lambda e: poly_degree_text.value = f"Polynomial Degree: {int(e.control.value)}"
    )
    
    poly_degree_text = ft.Text("Polynomial Degree: 1")
    
    poly_degree_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("Polynomial Features (Linear Regression only)", weight=ft.FontWeight.BOLD),
                ft.Row([poly_degree_slider, poly_degree_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text("Higher degrees can model more complex relationships but may overfit.")
            ],
            spacing=10
        ),
        visible=False,
        padding=10,
        border=ft.border.all(1, ft.colors.GREY_300),
        border_radius=10
    )
    
    # Model parameters based on selected model
    linear_params = ft.Container(
        content=ft.Column(
            [
                ft.Text("Linear Regression Parameters", weight=ft.FontWeight.BOLD),
                ft.Checkbox(label="Fit Intercept", value=True),
                ft.Text("Parameters will be automatically configured based on the data.")
            ],
            spacing=10
        ),
        visible=False,
        padding=10,
        border=ft.border.all(1, ft.colors.GREY_300),
        border_radius=10
    )
    
    svr_params = ft.Container(
        content=ft.Column(
            [
                ft.Text("SVR Parameters", weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    label="Kernel",
                    options=[
                        ft.dropdown.Option("linear", text="Linear"),
                        ft.dropdown.Option("poly", text="Polynomial"),
                        ft.dropdown.Option("rbf", text="RBF (Radial Basis Function)"),
                        ft.dropdown.Option("sigmoid", text="Sigmoid")
                    ],
                    value="rbf"
                ),
                ft.Slider(
                    min=0.1,
                    max=10.0,
                    divisions=20,
                    label="C: {value}",
                    value=1.0
                ),
                ft.Slider(
                    min=0.01,
                    max=1.0,
                    divisions=20,
                    label="Epsilon: {value}",
                    value=0.1
                ),
                ft.Text("C controls regularization, epsilon defines the margin of tolerance.")
            ],
            spacing=10
        ),
        visible=False,
        padding=10,
        border=ft.border.all(1, ft.colors.GREY_300),
        border_radius=10
    )
    
    elastic_params = ft.Container(
        content=ft.Column(
            [
                ft.Text("ElasticNet Parameters", weight=ft.FontWeight.BOLD),
                ft.Slider(
                    min=0.01,
                    max=1.0,
                    divisions=20,
                    label="Alpha: {value}",
                    value=1.0
                ),
                ft.Slider(
                    min=0.0,
                    max=1.0,
                    divisions=20,
                    label="L1 Ratio: {value}",
                    value=0.5
                ),
                ft.Text("Alpha controls regularization strength, L1 Ratio balances L1 vs L2 regularization.")
            ],
            spacing=10
        ),
        visible=False,
        padding=10,
        border=ft.border.all(1, ft.colors.GREY_300),
        border_radius=10
    )
    
    sgd_params = ft.Container(
        content=ft.Column(
            [
                ft.Text("SGD Parameters", weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    label="Loss Function",
                    options=[
                        ft.dropdown.Option("squared_loss", text="Squared Loss"),
                        ft.dropdown.Option("huber", text="Huber"),
                        ft.dropdown.Option("epsilon_insensitive", text="Epsilon Insensitive"),
                        ft.dropdown.Option("squared_epsilon_insensitive", text="Squared Epsilon Insensitive")
                    ],
                    value="squared_loss"
                ),
                ft.Dropdown(
                    label="Penalty",
                    options=[
                        ft.dropdown.Option("none", text="None"),
                        ft.dropdown.Option("l1", text="L1"),
                        ft.dropdown.Option("l2", text="L2"),
                        ft.dropdown.Option("elasticnet", text="ElasticNet")
                    ],
                    value="l2"
                ),
                ft.Slider(
                    min=0.0001,
                    max=0.1,
                    divisions=20,
                    label="Alpha: {value}",
                    value=0.0001
                ),
                ft.Text("Loss function determines the error measure, penalty adds regularization.")
            ],
            spacing=10
        ),
        visible=False,
        padding=10,
        border=ft.border.all(1, ft.colors.GREY_300),
        border_radius=10
    )
    
    # Container for all parameter containers
    param_containers = ft.Container(
        content=ft.Column(
            [
                poly_degree_container,
                linear_params,
                svr_params,
                elastic_params,
                sgd_params
            ],
            spacing=10
        )
    )
    
    # Update visible parameter container based on model selection
    def update_param_container(e):
        model_type = model_dropdown.value
        
        # Hide all containers first
        poly_degree_container.visible = False
        linear_params.visible = False
        svr_params.visible = False
        elastic_params.visible = False
        sgd_params.visible = False
        
        # Show relevant containers
        if model_type == "LinearRegression":
            poly_degree_container.visible = True
            linear_params.visible = True
        elif model_type == "SVR":
            svr_params.visible = True
        elif model_type == "ElasticNet":
            elastic_params.visible = True
        elif model_type == "SGD":
            sgd_params.visible = True
        
        # Update the page
        param_containers.update()
    
    # Set model dropdown on_change event
    model_dropdown.on_change = update_param_container
    
    # Helper function to get parameters based on model type
    def get_model_params():
        """Get model parameters based on selected model."""
        model_type = model_dropdown.value
        params = {}
        polynomial_degree = int(poly_degree_slider.value)
        
        if model_type == "LinearRegression":
            params = {
                "fit_intercept": linear_params.content.controls[1].value
            }
        elif model_type == "SVR":
            kernel_dropdown = svr_params.content.controls[1]
            c_slider = svr_params.content.controls[2]
            epsilon_slider = svr_params.content.controls[3]
            
            params = {
                "kernel": kernel_dropdown.value,
                "C": c_slider.value,
                "epsilon": epsilon_slider.value
            }
        elif model_type == "ElasticNet":
            alpha_slider = elastic_params.content.controls[1]
            l1_ratio_slider = elastic_params.content.controls[2]
            
            params = {
                "alpha": alpha_slider.value,
                "l1_ratio": l1_ratio_slider.value
            }
        elif model_type == "SGD":
            loss_dropdown = sgd_params.content.controls[1]
            penalty_dropdown = sgd_params.content.controls[2]
            alpha_slider = sgd_params.content.controls[3]
            
            params = {
                "loss": loss_dropdown.value,
                "penalty": penalty_dropdown.value,
                "alpha": alpha_slider.value
            }
        
        return params, polynomial_degree
    
    # Train button
    train_button = ft.ElevatedButton(
        text="Train Model",
        icon=ft.icons.PLAY_ARROW,
        on_click=lambda _: handle_train_click()
    )
    
    # Handle train button click
    def handle_train_click():
        """Handle train button click."""
        model_type = model_dropdown.value
        
        if not model_type:
            # Show error message
            ft.page.snack_bar = ft.SnackBar(content=ft.Text("Please select a model type"))
            ft.page.snack_bar.open = True
            ft.page.update()
            return
        
        # Get model parameters
        params, polynomial_degree = get_model_params()
        
        # Call handle_train callback
        handle_train(model_type, params, polynomial_degree)
    
    # Create file info card
    file_info = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.INSERT_DRIVE_FILE, size=24, color=ft.colors.BLUE),
                            ft.Text("File Information", weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Text(f"Filename: {file['filename']}"),
                    ft.Text(f"Status: {file['status'].capitalize()}"),
                    ft.Text(f"Upload Date: {file['upload_date'].split('T')[0]}")
                ],
                spacing=10
            ),
            padding=20
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
                            ft.Text("Model Training Instructions", weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Text(
                        "1. Select a model type from the dropdown\n"
                        "2. Configure the model parameters\n"
                        "3. For Linear Regression, adjust the polynomial degree\n"
                        "4. Click 'Train Model' to start training\n"
                        "5. After training, visualizations will be displayed"
                    )
                ],
                spacing=10
            ),
            padding=20
        )
    )
    
    # Create comparison card
    comparison_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.COMPARE, size=24, color=ft.colors.BLUE),
                            ft.Text("Model Comparison", weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Text(
                        "• Linear Regression: Simple, fast, works well for linear relationships\n"
                        "• SVR: Handles non-linear data, robust to outliers\n"
                        "• ElasticNet: Good for data with many features, prevents overfitting\n"
                        "• SGD: Efficient for large datasets, adaptable to different loss functions"
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
                    ft.Text("Train Model", size=24, weight=ft.FontWeight.BOLD),
                    train_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            file_info,
            ft.Divider(),
            instructions_card,
            ft.Divider(),
            ft.Text("Select Model and Parameters", size=18, weight=ft.FontWeight.BOLD),
            model_dropdown,
            param_containers,
            ft.Divider(),
            comparison_card
        ],
        spacing=20
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