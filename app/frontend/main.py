import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Nissan App"

    # Definir listas y controles al inicio
    file_list = ft.Column()
    preprocess_list = ft.Column()
    train_list = ft.Column()

    # Función para manejar el login
    def handle_login(e):
        response = requests.post("http://127.0.0.1:8000/login", json={
            "username": username_field.value,
            "password": password_field.value
        })
        if response.status_code == 200:
            page.snack_bar = ft.SnackBar(ft.Text("Inicio de sesión exitoso"))
            page.snack_bar.open = True
            page.update()
            show_file_management()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Error en el inicio de sesión"))
            page.snack_bar.open = True
            page.update()

    # Página de login
    username_field = ft.TextField(label="Usuario")
    password_field = ft.TextField(label="Contraseña", password=True)
    login_button = ft.ElevatedButton("Iniciar sesión", on_click=handle_login)

    page.add(
        ft.Column([
            ft.Text("Iniciar sesión", size=24),
            username_field,
            password_field,
            login_button
        ])
    )

    # Función para mostrar la gestión de archivos
    def show_file_management():
        page.controls.clear()
        page.add(ft.Text("Gestión de Archivos", size=24))
        # Aquí se agregarán más controles para subir, listar y gestionar archivos
        page.update()

        # Función para manejar la subida de archivos
        def handle_upload(e):
            if file_picker.result is not None:
                file_path = file_picker.result[0]
                with open(file_path, "rb") as f:
                    response = requests.post("http://127.0.0.1:8000/upload", files={"file": f})
                if response.status_code == 200:
                    page.snack_bar = ft.SnackBar(ft.Text("Archivo subido exitosamente"))
                    page.snack_bar.open = True
                    page.update()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Error al subir el archivo"))
                    page.snack_bar.open = True
                    page.update()

        # Función para listar archivos
        def list_files():
            response = requests.get("http://127.0.0.1:8000/files")
            if response.status_code == 200:
                files = response.json()
                file_list.controls.clear()
                for file in files:
                    file_list.controls.append(ft.Text(file["filename"]))
                page.update()

        # Función para manejar el preprocesamiento de datos
        def preprocess_file(file_id):
            response = requests.post(f"http://127.0.0.1:8000/preprocess/{file_id}")
            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Archivo preprocesado exitosamente"))
                page.snack_bar.open = True
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error al preprocesar el archivo"))
                page.snack_bar.open = True
                page.update()

        # Agregar botón para preprocesar archivos
        def add_preprocess_buttons():
            response = requests.get("http://127.0.0.1:8000/files")
            if response.status_code == 200:
                files = response.json()
                preprocess_list.controls.clear()
                for file in files:
                    preprocess_list.controls.append(
                        ft.Row([
                            ft.Text(file["filename"]),
                            ft.ElevatedButton("Preprocesar", on_click=lambda e, file_id=file["id"]: preprocess_file(file_id))
                        ])
                    )
                page.update()

        # Función para manejar el entrenamiento de modelos
        def train_model(file_id, model_type, params):
            response = requests.post(f"http://127.0.0.1:8000/train/{file_id}", json={"model_type": model_type, "params": params})
            if response.status_code == 200:
                result = response.json()
                page.snack_bar = ft.SnackBar(ft.Text(f"Modelo entrenado: MSE={result['mse']}, R2={result['r2']}"))
                page.snack_bar.open = True
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error al entrenar el modelo"))
                page.snack_bar.open = True
                page.update()

        # Botón para entrenar modelo
        def add_train_buttons():
            response = requests.get("http://127.0.0.1:8000/files")
            if response.status_code == 200:
                files = response.json()
                train_list.controls.clear()
                for file in files:
                    train_list.controls.append(
                        ft.Row([
                            ft.Text(file["filename"]),
                            ft.ElevatedButton(
                                "Entrenar",
                                on_click=lambda e, file_id=file["id"]: train_model(
                                    file_id,
                                    model_dropdown.value,
                                    eval(param_field.value)
                                )
                            )
                        ])
                    )
                page.update()

        # Controles para subir archivos
        file_picker = ft.FilePicker(on_result=handle_upload)
        upload_button = ft.ElevatedButton("Subir archivo", on_click=lambda _: file_picker.pick_files())
        refresh_button = ft.ElevatedButton("Actualizar lista", on_click=lambda _: list_files())

        # Controles para preprocesar archivos
        preprocess_button = ft.ElevatedButton("Cargar archivos para preprocesar", on_click=lambda _: add_preprocess_buttons())

        # Controles para entrenar modelos
        model_dropdown = ft.Dropdown(
            label="Seleccionar modelo",
            options=[
                ft.DropdownOption("LinearRegression"),
                ft.DropdownOption("SVR"),
                ft.DropdownOption("ElasticNet"),
                ft.DropdownOption("SGD")
            ]
        )
        param_field = ft.TextField(label="Parámetros (JSON)")
        train_button = ft.ElevatedButton("Cargar archivos para entrenar", on_click=lambda _: add_train_buttons())

        # Agregar controles a la página
        page.controls.extend([
            ft.Row([upload_button, refresh_button]),
            file_list,
            preprocess_button,
            preprocess_list,
            model_dropdown,
            param_field,
            train_button,
            train_list
        ])

ft.app(target=main)
