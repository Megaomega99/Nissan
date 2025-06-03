import flet as ft
import requests
import io

# Configuración base
BASE_URL = "http://localhost:8000/api/v1"
token = None

def show_message(page: ft.Page, msg: str):
    # Muestra Snackbar sin color personalizado para compatibilidad
    page.snack_bar = ft.SnackBar(content=ft.Text(msg), open=True)
    page.update()


def main(page: ft.Page):
    page.title = "Plataforma ML Nissan"
    page.window_width = 900
    page.window_height = 700
    page.padding = 20
    page.scroll = "auto"
    page.snack_bar = ft.SnackBar()

    # Refs
    username = ft.Ref[ft.TextField]()
    password = ft.Ref[ft.TextField]()
    email_reg = ft.Ref[ft.TextField]()
    username_reg = ft.Ref[ft.TextField]()
    full_name = ft.Ref[ft.TextField]()
    password_reg = ft.Ref[ft.TextField]()

    def login(e):
        global token
        data = {"username": username.current.value, "password": password.current.value}
        resp = requests.post(f"{BASE_URL}/auth/login", data=data)
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            show_message(page, "Login exitoso")
            page.clean()
            page.add(main_tabs(page))
        else:
            show_message(page, "Error al iniciar sesión")

    def register(e):
        payload = {
            "email": email_reg.current.value,
            "username": username_reg.current.value,
            "full_name": full_name.current.value,
            "password": password_reg.current.value
        }
        resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
        if resp.status_code == 201:
            show_message(page, "Registro exitoso, ya puedes iniciar sesión")
        else:
            show_message(page, f"Error: {resp.text}", ft.colors.RED)

    # UI login y registro
    page.add(
        ft.Column([
            ft.Text("Bienvenido a la Plataforma ML Nissan", size=30, weight="bold"),
            ft.Divider(height=20),
            ft.Text("Iniciar Sesión", size=24),
            ft.TextField(ref=username, label="Usuario o Email", width=300),
            ft.TextField(ref=password, label="Contraseña", password=True, can_reveal_password=True, width=300),
            ft.ElevatedButton("Iniciar Sesión", on_click=login),
            ft.Divider(height=30),
            ft.Text("Registro", size=24),
            ft.TextField(ref=full_name, label="Nombre Completo", width=300),
            ft.TextField(ref=email_reg, label="Email", width=300),
            ft.TextField(ref=username_reg, label="Usuario", width=300),
            ft.TextField(ref=password_reg, label="Contraseña", password=True, can_reveal_password=True, width=300),
            ft.ElevatedButton("Registrarme", on_click=register)
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )


def main_tabs(page: ft.Page):
    return ft.Tabs(
        tabs=[
            ft.Tab(text="Perfil", content=perfil_view(page)),
            ft.Tab(text="Archivos", content=files_view(page)),
            ft.Tab(text="Preprocesar", content=preprocess_view(page)),
            ft.Tab(text="Entrenar", content=train_view(page)),
            ft.Tab(text="Modelos", content=models_view(page)),
            ft.Tab(text="Predecir", content=predict_view(page)),
        ], expand=1
    )


def perfil_view(page: ft.Page):
    container = ft.Column(spacing=10)
    def cargar_perfil(e=None):
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if resp.status_code == 200:
            u = resp.json()
            container.controls = [
                ft.Text(f"Usuario: {u['username']}", size=18),
                ft.Text(f"Email: {u['email']}", size=18),
                ft.Text(f"Nombre: {u['full_name']}", size=18),
            ]
        else:
            container.controls = [ft.Text("Error al cargar perfil", color=ft.colors.RED)]
        page.update()
    cargar_perfil()
    return ft.Container(content=container, padding=20)


def files_view(page: ft.Page):
    list_view = ft.ListView(expand=1, spacing=5)
    file_picker = ft.FilePicker(on_result=lambda e: upload_file(e, page, list_view))
    page.overlay.append(file_picker)

    def refresh_files():
        list_view.controls.clear()
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/files/list", headers=headers)
        if resp.status_code == 200:
            for f in resp.json():
                list_view.controls.append(ft.ListTile(title=f['filename'], subtitle=f"ID: {f['id']}"))
        else:
            show_message(page, "Error al listar archivos", ft.colors.RED)
        page.update()

    # Toolbar sin iconos para compatibilidad web
    toolbar = ft.Row([
        ft.ElevatedButton("Subir CSV", on_click=lambda e: file_picker.pick_files(allow_multiple=False)),
        ft.ElevatedButton("Refrescar lista", on_click=lambda e: refresh_files()),
    ])
    refresh_files()
    return ft.Column([toolbar, list_view], expand=1, spacing=10)


def upload_file(e, page: ft.Page, list_view: ft.ListView):
    if e.files:
        file = e.files[0]
        with open(file.path, "rb") as fp:
            files_param = {"file": (file.name, fp, "text/csv")}
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.post(f"{BASE_URL}/files/upload", files=files_param, headers=headers)
            if resp.status_code == 201:
                show_message(page, "Archivo subido con éxito")
                # refrescar
                files = requests.get(f"{BASE_URL}/files/list", headers=headers)
                if files.status_code == 200:
                    list_view.controls.clear()
                    for f in files.json():
                        list_view.controls.append(ft.ListTile(title=f['filename'], subtitle=f"ID: {f['id']}"))
                    page.update()
            else:
                show_message(page, "Error al subir archivo", ft.colors.RED)
    else:
        show_message(page, "No se seleccionó ningún archivo", ft.colors.RED)


def preprocess_view(page: ft.Page):
    return ft.Text("Sección de Preprocesamiento - Próximamente", size=16)

def train_view(page: ft.Page):
    return ft.Text("Sección de Entrenamiento - Próximamente", size=16)

def models_view(page: ft.Page):
    return ft.Text("Listado de Modelos - Próximamente", size=16)

def predict_view(page: ft.Page):
    return ft.Text("Sección de Predicciones - Próximamente", size=16)


if __name__ == "__main__":
    # Ejecutar en modo web en puerto 8501
    ft.app(target=main, view=ft.WEB_BROWSER, port=8501)