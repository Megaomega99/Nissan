import flet as ft
import requests
import io
import os
from typing import Optional, Dict, Any, List
import json

# Base URL configuration from environment
BASE_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
token: Optional[str] = None


def show_message(page: ft.Page, msg: str, color: str = None) -> None:
    """Display a snackbar message to the user."""
    if color:
        page.snack_bar.content = ft.Text(msg, color=color)
    else:
        page.snack_bar.content = ft.Text(msg)
    page.snack_bar.open = True
    page.update()


def main(page: ft.Page) -> None:
    """Initialize the main application page."""
    page.title = "Plataforma ML Nissan"
    page.window_width = 900
    page.window_height = 700
    page.padding = 20
    page.scroll = "auto"
    
    # Top app bar
    page.appbar = ft.AppBar(
        title=ft.Text("Plataforma ML Nissan"),
        center_title=True
    )
    
    # Initialize snackbar
    page.snack_bar = ft.SnackBar(ft.Text(""), open=False)

    # Refs for login/register fields
    username = ft.Ref[ft.TextField]()
    password = ft.Ref[ft.TextField]()
    email_reg = ft.Ref[ft.TextField]()
    username_reg = ft.Ref[ft.TextField]()
    full_name = ft.Ref[ft.TextField]()
    password_reg = ft.Ref[ft.TextField]()

    def login(e) -> None:
        """Handle user login."""
        global token
        data = {
            "username": username.current.value,
            "password": password.current.value
        }
        try:
            resp = requests.post(f"{BASE_URL}/auth/login", data=data)
            if resp.status_code == 200:
                token = resp.json()["access_token"]
                show_message(page, "Login exitoso", "green")
                page.clean()
                page.add(main_tabs(page))
            else:
                error_detail = resp.json().get("detail", "Error desconocido")
                show_message(page, f"Error: {error_detail}", "red")
        except Exception as ex:
            show_message(page, f"Error de conexión: {str(ex)}", "red")

    def register(e) -> None:
        """Handle user registration."""
        payload = {
            "email": email_reg.current.value,
            "username": username_reg.current.value,
            "full_name": full_name.current.value,
            "password": password_reg.current.value
        }
        try:
            resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
            if resp.status_code == 201:
                show_message(page, "Registro exitoso, ya puedes iniciar sesión", "green")
                # Clear registration fields
                email_reg.current.value = ""
                username_reg.current.value = ""
                full_name.current.value = ""
                password_reg.current.value = ""
                page.update()
            else:
                error_detail = resp.json().get("detail", "Error desconocido")
                show_message(page, f"Error: {error_detail}", "red")
        except Exception as ex:
            show_message(page, f"Error de conexión: {str(ex)}", "red")

    # Login and registration UI
    page.add(
        ft.Column([
            ft.Text("Bienvenido a la Plataforma ML Nissan", size=30, weight="bold"),
            ft.Divider(height=20),
            ft.Text("Iniciar Sesión", size=24),
            ft.TextField(ref=username, label="Usuario o Email", width=300),
            ft.TextField(ref=password, label="Contraseña", password=True, 
                        can_reveal_password=True, width=300),
            ft.ElevatedButton("Iniciar Sesión", on_click=login),
            ft.Divider(height=30),
            ft.Text("Registro", size=24),
            ft.TextField(ref=full_name, label="Nombre Completo", width=300),
            ft.TextField(ref=email_reg, label="Email", width=300),
            ft.TextField(ref=username_reg, label="Usuario", width=300),
            ft.TextField(ref=password_reg, label="Contraseña", password=True, 
                        can_reveal_password=True, width=300),
            ft.ElevatedButton("Registrarme", on_click=register)
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )


def main_tabs(page: ft.Page) -> ft.Tabs:
    """Create the main tabbed interface."""
    return ft.Tabs(
        tabs=[
            ft.Tab(text="Perfil", content=perfil_view(page)),
            ft.Tab(text="Archivos", content=files_view(page)),
            ft.Tab(text="Preprocesar", content=preprocess_view(page)),
            ft.Tab(text="Entrenar", content=train_view(page)),
            ft.Tab(text="Modelos", content=models_view(page)),
            ft.Tab(text="Predecir", content=predict_view(page)),
        ], 
        expand=1
    )


def perfil_view(page: ft.Page) -> ft.Container:
    """User profile view."""
    container = ft.Column(spacing=10)
    
    def cargar_perfil(e=None) -> None:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            if resp.status_code == 200:
                u = resp.json()
                container.controls = [
                    ft.Text(f"Usuario: {u['username']}", size=18),
                    ft.Text(f"Email: {u['email']}", size=18),
                    ft.Text(f"Nombre: {u.get('full_name', 'N/A')}", size=18),
                ]
            else:
                container.controls = [ft.Text("Error al cargar perfil", color="red")]
        except Exception as ex:
            container.controls = [ft.Text(f"Error de conexión: {str(ex)}", color="red")]
        page.update()

    def logout(e) -> None:
        """Handle logout."""
        global token
        token = None
        show_message(page, "Sesión cerrada")
        page.clean()
        main(page)

    cargar_perfil()
    
    return ft.Container(
        content=ft.Column([
            container,
            ft.ElevatedButton("Cerrar Sesión", on_click=logout)
        ], spacing=10),
        padding=20
    )


def files_view(page: ft.Page) -> ft.Container:
    """File management view."""
    list_view = ft.ListView(expand=1, spacing=5)
    
    def on_file_result(e) -> None:
        upload_file(e, page, list_view, refresh_files)
    
    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    def refresh_files() -> None:
        """Refresh the file list."""
        list_view.controls.clear()
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(f"{BASE_URL}/files/list", headers=headers)
            if resp.status_code == 200:
                files = resp.json()
                if not files:
                    list_view.controls.append(
                        ft.Text("No hay archivos subidos", italic=True)
                    )
                else:
                    for f in files:
                        list_view.controls.append(
                            ft.ListTile(
                                title=ft.Text(f['original_filename']),
                                subtitle=ft.Text(
                                    f"ID: {f['id']} | Tamaño: {f['file_size']} bytes | "
                                    f"Filas: {f.get('rows_count', 'N/A')}"
                                ),
                                trailing=ft.IconButton(
                                    ft.icons.DELETE,
                                    on_click=lambda e, fid=f['id']: delete_file(fid)
                                )
                            )
                        )
            else:
                show_message(page, "Error al listar archivos", "red")
        except Exception as ex:
            show_message(page, f"Error de conexión: {str(ex)}", "red")
        page.update()

    def delete_file(file_id: int) -> None:
        """Delete a file."""
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.delete(f"{BASE_URL}/files/{file_id}", headers=headers)
            if resp.status_code == 204:
                show_message(page, "Archivo eliminado", "green")
                refresh_files()
            else:
                show_message(page, "Error al eliminar archivo", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    toolbar = ft.Row([
        ft.ElevatedButton(
            "Subir CSV", 
            on_click=lambda e: file_picker.pick_files(
                allowed_extensions=["csv"], 
                allow_multiple=False
            )
        ),
        ft.ElevatedButton("Refrescar lista", on_click=lambda e: refresh_files()),
    ])
    
    refresh_files()
    
    return ft.Container(
        content=ft.Column([toolbar, list_view], expand=1, spacing=10),
        padding=20,
        expand=1
    )


def upload_file(e, page: ft.Page, list_view: ft.ListView, refresh_fn) -> None:
    """Handle file upload."""
    if e.files:
        file = e.files[0]
        try:
            # Read file data
            if file.path:
                with open(file.path, "rb") as f:
                    file_bytes = f.read()
            else:
                file_bytes = file.read_bytes()
            
            buf = io.BytesIO(file_bytes)
            files_param = {"file": (file.name, buf, "text/csv")}
            headers = {"Authorization": f"Bearer {token}"}
            
            resp = requests.post(
                f"{BASE_URL}/files/upload", 
                files=files_param, 
                headers=headers
            )
            
            if resp.status_code == 201:
                show_message(page, "Archivo subido con éxito", "green")
                refresh_fn()
            else:
                error_detail = resp.json().get("detail", "Error desconocido")
                show_message(page, f"Error: {error_detail}", "red")
        except Exception as ex:
            show_message(page, f"Error al subir archivo: {str(ex)}", "red")
    else:
        show_message(page, "No se seleccionó ningún archivo", "red")


def preprocess_view(page: ft.Page) -> ft.Container:
    """Data preprocessing view."""
    file_dd = ft.Dropdown(label="Seleccionar archivo", width=300)
    remove_nulls = ft.Checkbox(label="Eliminar valores nulos", value=True)
    fill_nulls = ft.Checkbox(label="Rellenar valores nulos", value=False)
    fill_method = ft.Dropdown(
        label="Método de relleno",
        options=[
            ft.dropdown.Option("mean", "Media"),
            ft.dropdown.Option("median", "Mediana"),
            ft.dropdown.Option("mode", "Moda"),
            ft.dropdown.Option("zero", "Cero"),
        ],
        value="mean",
        width=150,
    )
    drop_dups = ft.Checkbox(label="Eliminar duplicados", value=True)
    remove_outliers = ft.Checkbox(label="Eliminar outliers", value=False)
    result_panel = ft.Column(expand=1, scroll="auto")

    def load_files() -> None:
        """Load available files."""
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(f"{BASE_URL}/files/list", headers=headers)
            if resp.status_code == 200:
                files = resp.json()
                file_dd.options = [
                    ft.dropdown.Option(str(f['id']), f['original_filename']) 
                    for f in files
                ]
                page.update()
            else:
                show_message(page, "Error cargando archivos", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    def clean_data(e) -> None:
        """Clean selected data file."""
        if not file_dd.value:
            show_message(page, "Seleccione un archivo", "red")
            return
        
        payload = {
            "remove_nulls": remove_nulls.value,
            "fill_nulls": fill_nulls.value,
            "fill_method": fill_method.value,
            "drop_duplicates": drop_dups.value,
            "remove_outliers": remove_outliers.value
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.post(
                f"{BASE_URL}/preprocessing/{file_dd.value}/clean",
                json=payload,
                headers=headers
            )
            if resp.status_code == 200:
                stats = resp.json()
                # Show statistics and preview
                result_panel.controls = [
                    ft.Text("Estadísticas de procesamiento:", size=18, weight="bold"),
                    ft.Text(f"Filas originales: {stats.get('original_rows', 'N/A')}"),
                    ft.Text(f"Filas procesadas: {stats.get('processed_rows', 'N/A')}"),
                    ft.Text(f"Filas eliminadas: {stats.get('removed_rows', 'N/A')}"),
                    ft.Divider(),
                    ft.Text("Vista previa de datos procesados:", size=16, weight="bold")
                ]
                
                # Display preview data as table
                preview_data = stats.get('preview', [])
                if preview_data:
                    columns = list(preview_data[0].keys())
                    table_rows = [
                        ft.DataRow(
                            cells=[ft.DataCell(ft.Text(str(row[col]))) for col in columns]
                        ) for row in preview_data
                    ]
                    data_table = ft.DataTable(
                        columns=[ft.DataColumn(ft.Text(col)) for col in columns],
                        rows=table_rows
                    )
                    result_panel.controls.append(data_table)
                
                show_message(page, "Datos procesados exitosamente", "green")
            else:
                error_detail = resp.json().get("detail", "Error desconocido")
                show_message(page, f"Error: {error_detail}", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")
        page.update()

    def analyze(e) -> None:
        """Analyze selected file."""
        if not file_dd.value:
            show_message(page, "Seleccione un archivo", "red")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(
                f"{BASE_URL}/preprocessing/{file_dd.value}/analysis",
                headers=headers
            )
            if resp.status_code == 200:
                analysis = resp.json()
                # Display analysis results
                result_panel.controls = [
                    ft.Text("Análisis del archivo:", size=18, weight="bold"),
                    ft.Text(f"Total de filas: {analysis['metadata']['rows_count']}"),
                    ft.Text(f"Columnas: {', '.join(analysis['metadata']['columns'])}"),
                    ft.Divider(),
                    ft.Text("Estadísticas por columna:", size=16, weight="bold")
                ]
                
                # Display column statistics
                for col, stats in analysis.get('column_stats', {}).items():
                    result_panel.controls.extend([
                        ft.Text(f"\n{col}:", weight="bold"),
                        ft.Text(f"  Min: {stats.get('min', 'N/A')}"),
                        ft.Text(f"  Max: {stats.get('max', 'N/A')}"),
                        ft.Text(f"  Media: {stats.get('mean', 'N/A')}"),
                        ft.Text(f"  Mediana: {stats.get('median', 'N/A')}"),
                        ft.Text(f"  Valores nulos: {stats.get('null_count', 'N/A')}")
                    ])
                
                show_message(page, "Análisis completado", "green")
            else:
                show_message(page, "Error en análisis", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")
        page.update()

    load_files()
    
    toolbar = ft.Row([
        file_dd, 
        remove_nulls, 
        fill_nulls, 
        fill_method, 
        drop_dups, 
        remove_outliers
    ], spacing=10, wrap=True)
    
    buttons = ft.Row([
        ft.ElevatedButton("Limpiar Datos", on_click=clean_data),
        ft.ElevatedButton("Analizar", on_click=analyze)
    ], spacing=10)
    
    return ft.Container(
        content=ft.Column([
            toolbar, 
            buttons, 
            ft.Divider(), 
            result_panel
        ], expand=1, spacing=20),
        padding=20,
        expand=1
    )


def train_view(page: ft.Page) -> ft.Container:
    """Model training view."""
    file_dd = ft.Dropdown(label="Archivo", width=300)
    model_dd = ft.Dropdown(
        label="Algoritmo",
        options=[
            ft.dropdown.Option("linear_regression", "Regresión Lineal"),
            ft.dropdown.Option("svr", "Support Vector Regression"),
            ft.dropdown.Option("elasticnet", "ElasticNet"),
            ft.dropdown.Option("sgd", "Stochastic Gradient Descent"),
        ],
        value="linear_regression",
        width=250,
    )
    model_name = ft.TextField(label="Nombre del modelo", width=300)
    index_column = ft.TextField(label="Columna índice (X)", width=200)
    target_column = ft.TextField(label="Columna objetivo (Y)", width=200)
    parameters_text = ft.TextField(
        label="Parámetros (JSON)", 
        width=400, 
        value='{}',
        multiline=True
    )
    result_panel = ft.Column()

    def load_files() -> None:
        """Load available files."""
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(f"{BASE_URL}/files/list", headers=headers)
            if resp.status_code == 200:
                files = resp.json()
                file_dd.options = [
                    ft.dropdown.Option(str(f['id']), f['original_filename']) 
                    for f in files
                ]
                page.update()
            else:
                show_message(page, "Error cargando archivos", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    def train(e) -> None:
        """Train a model."""
        if not all([file_dd.value, index_column.value, target_column.value]):
            show_message(page, "Complete todos los campos obligatorios", "red")
            return
        
        try:
            # Parse parameters
            parameters = json.loads(parameters_text.value)
        except json.JSONDecodeError:
            show_message(page, "Parámetros JSON inválidos", "red")
            return
        
        payload = {
            "file_id": int(file_dd.value),
            "model_type": model_dd.value,
            "name": model_name.value or f"Modelo {model_dd.value}",
            "index_column": index_column.value,
            "target_column": target_column.value,
            "parameters": parameters
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.post(
                f"{BASE_URL}/models/train", 
                json=payload, 
                headers=headers
            )
            if resp.status_code == 202:
                result = resp.json()
                show_message(page, "Entrenamiento iniciado", "green")
                result_panel.controls = [
                    ft.Text("Entrenamiento en proceso:", size=16, weight="bold"),
                    ft.Text(f"ID del modelo: {result['model_id']}"),
                    ft.Text(f"ID de tarea: {result['task_id']}"),
                    ft.Text(f"Estado: {result['status']}"),
                    ft.Text(result['message'])
                ]
                page.update()
            else:
                error_detail = resp.json().get("detail", "Error desconocido")
                show_message(page, f"Error: {error_detail}", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    load_files()
    
    form = ft.Column([
        file_dd,
        model_dd,
        model_name,
        ft.Row([index_column, target_column], spacing=10),
        parameters_text,
        ft.ElevatedButton("Entrenar Modelo", on_click=train)
    ], spacing=10)
    
    return ft.Container(
        content=ft.Column([
            form, 
            ft.Divider(), 
            result_panel
        ], expand=1, spacing=20),
        padding=20,
        expand=1
    )


def models_view(page: ft.Page) -> ft.Container:
    """Model management view."""
    list_view = ft.ListView(expand=1, spacing=5)
    
    def refresh() -> None:
        """Refresh model list."""
        list_view.controls.clear()
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(f"{BASE_URL}/models/list", headers=headers)
            if resp.status_code == 200:
                models = resp.json()
                if not models:
                    list_view.controls.append(
                        ft.Text("No hay modelos entrenados", italic=True)
                    )
                else:
                    for m in models:
                        # Create status icon
                        if m['training_status'] == 'completed':
                            status_icon = ft.Icon(ft.icons.CHECK_CIRCLE, color="green")
                        elif m['training_status'] == 'failed':
                            status_icon = ft.Icon(ft.icons.ERROR, color="red")
                        else:
                            status_icon = ft.Icon(ft.icons.PENDING, color="orange")
                        
                        list_view.controls.append(
                            ft.ListTile(
                                leading=status_icon,
                                title=ft.Text(f"{m['name']} (ID: {m['id']})"),
                                subtitle=ft.Text(
                                    f"Tipo: {m['model_type']} | "
                                    f"R²: {m['metrics']['r2']:.4f if m['metrics']['r2'] else 'N/A'}"
                                ),
                                trailing=ft.Row([
                                    ft.IconButton(
                                        ft.icons.INFO,
                                        on_click=lambda e, mid=m['id']: show_details(mid),
                                        tooltip="Ver detalles"
                                    ),
                                    ft.IconButton(
                                        ft.icons.DELETE,
                                        on_click=lambda e, mid=m['id']: delete_model(mid),
                                        icon_color="red",
                                        tooltip="Eliminar"
                                    )
                                ], tight=True)
                            )
                        )
            else:
                show_message(page, "Error listando modelos", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")
        page.update()
    
    def show_details(model_id: int) -> None:
        """Show model details."""
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(f"{BASE_URL}/models/{model_id}", headers=headers)
            if resp.status_code == 200:
                model = resp.json()
                metrics = model['metrics']
                
                content = ft.Column([
                    ft.Text(f"Nombre: {model['name']}", weight="bold"),
                    ft.Text(f"Tipo: {model['model_type']}"),
                    ft.Text(f"Estado: {model['training_status']}"),
                    ft.Text(f"Columna índice: {model['index_column']}"),
                    ft.Text(f"Columna objetivo: {model['target_column']}"),
                    ft.Divider(),
                    ft.Text("Métricas:", weight="bold"),
                    ft.Text(f"MAE: {metrics['mae']:.4f}" if metrics['mae'] else "MAE: N/A"),
                    ft.Text(f"MSE: {metrics['mse']:.4f}" if metrics['mse'] else "MSE: N/A"),
                    ft.Text(f"RMSE: {metrics['rmse']:.4f}" if metrics['rmse'] else "RMSE: N/A"),
                    ft.Text(f"R²: {metrics['r2']:.4f}" if metrics['r2'] else "R²: N/A"),
                ], scroll="auto")
                
                dlg = ft.AlertDialog(
                    title=ft.Text("Detalles del Modelo"),
                    content=content,
                    actions=[
                        ft.TextButton("Cerrar", on_click=lambda e: close_dialog())
                    ]
                )
                
                def close_dialog():
                    dlg.open = False
                    page.update()
                
                page.dialog = dlg
                dlg.open = True
                page.update()
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")
    
    def delete_model(model_id: int) -> None:
        """Delete a model."""
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.delete(f"{BASE_URL}/models/{model_id}", headers=headers)
            if resp.status_code == 204:
                show_message(page, "Modelo eliminado", "green")
                refresh()
            else:
                show_message(page, "Error al eliminar modelo", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    toolbar = ft.Row([
        ft.ElevatedButton("Refrescar", on_click=lambda e: refresh())
    ], spacing=10)
    
    refresh()
    
    return ft.Container(
        content=ft.Column([toolbar, list_view], expand=1, spacing=10),
        padding=20,
        expand=1
    )


def predict_view(page: ft.Page) -> ft.Container:
    """Prediction view."""
    model_dd = ft.Dropdown(label="Modelo", width=300)
    indices_field = ft.TextField(
        label="Valores de índice (separados por coma)", 
        width=400,
        hint_text="Ej: 100,101,102,103"
    )
    predict_all = ft.Checkbox(label="Predecir todo el dataset", value=False)
    result_panel = ft.Column(expand=1, scroll="auto")
    
    def load_models() -> None:
        """Load trained models."""
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(f"{BASE_URL}/models/list", headers=headers)
            if resp.status_code == 200:
                models = resp.json()
                # Only show completed models
                trained_models = [m for m in models if m['is_trained']]
                model_dd.options = [
                    ft.dropdown.Option(
                        str(m['id']), 
                        f"{m['name']} (ID: {m['id']})"
                    ) 
                    for m in trained_models
                ]
                page.update()
            else:
                show_message(page, "Error cargando modelos", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")
    
    def predict(e) -> None:
        """Make predictions."""
        if not model_dd.value:
            show_message(page, "Seleccione un modelo", "red")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            if predict_all.value:
                # Predict for entire dataset
                payload = {}
            else:
                # Predict for specific values
                if not indices_field.value:
                    show_message(page, "Ingrese valores de índice", "red")
                    return
                
                indices = [float(v.strip()) for v in indices_field.value.split(',')]
                payload = {"indices": indices}
            
            resp = requests.post(
                f"{BASE_URL}/models/{model_dd.value}/predict",
                json=payload,
                headers=headers
            )
            
            if resp.status_code == 200:
                predictions = resp.json()
                result_panel.controls = [
                    ft.Text("Resultados de Predicción:", size=18, weight="bold")
                ]
                
                if "original" in predictions:
                    # Full dataset prediction
                    original = predictions['original']
                    projection = predictions['projection']
                    
                    result_panel.controls.extend([
                        ft.Text("Predicciones sobre datos originales:", weight="bold"),
                        ft.Text(f"Puntos de datos: {len(original['indices'])}")
                    ])
                    
                    # Show sample predictions
                    if len(original['indices']) > 5:
                        result_panel.controls.append(
                            ft.Text("Muestra de predicciones (primeras 5):")
                        )
                        for i in range(5):
                            result_panel.controls.append(
                                ft.Text(
                                    f"  Índice: {original['indices'][i]:.2f}, "
                                    f"Predicción: {original['predictions'][i]:.2f}, "
                                    f"Real: {original['actual_values'][i]:.2f}"
                                )
                            )
                    
                    result_panel.controls.extend([
                        ft.Divider(),
                        ft.Text("Proyección futura:", weight="bold"),
                        ft.Text(f"Puntos proyectados: {len(projection['indices'])}")
                    ])
                    
                    # Show sample projections
                    for i in range(min(5, len(projection['indices']))):
                        result_panel.controls.append(
                            ft.Text(
                                f"  Índice: {projection['indices'][i]:.2f}, "
                                f"Predicción: {projection['predictions'][i]:.2f}"
                            )
                        )
                else:
                    # Specific values prediction
                    indices = predictions['indices']
                    preds = predictions['predictions']
                    
                    for i, pred in zip(indices, preds):
                        result_panel.controls.append(
                            ft.Text(f"Índice: {i:.2f}, Predicción: {pred:.2f}")
                        )
                
                show_message(page, "Predicción completada", "green")
            else:
                error_detail = resp.json().get("detail", "Error desconocido")
                show_message(page, f"Error: {error_detail}", "red")
        except ValueError as ve:
            show_message(page, "Error: Los valores deben ser números", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")
        
        page.update()
    
    def on_predict_all_change(e) -> None:
        """Handle predict all checkbox change."""
        indices_field.disabled = predict_all.value
        page.update()
    
    predict_all.on_change = on_predict_all_change
    load_models()
    
    form = ft.Column([
        model_dd,
        predict_all,
        indices_field,
        ft.ElevatedButton("Realizar Predicción", on_click=predict)
    ], spacing=10)
    
    return ft.Container(
        content=ft.Column([
            form, 
            ft.Divider(), 
            result_panel
        ], expand=1, spacing=20),
        padding=20,
        expand=1
    )


if __name__ == "__main__":
    # Run in web mode on port 8501
    ft.app(target=main, view=ft.WEB_BROWSER, port=8501)