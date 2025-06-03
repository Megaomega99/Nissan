import flet as ft
import requests
import io
import os  # nueva importación

# Configuración base desde entorno
BASE_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
token = None

def show_message(page: ft.Page, msg: str, color: str = None):
    # Muestra Snackbar sin recrear, actualiza contenido y abre
    if color:
        page.snack_bar.content = ft.Text(msg, color=color)
    else:
        page.snack_bar.content = ft.Text(msg)
    page.snack_bar.open = True
    page.update()


def main(page: ft.Page):
    page.title = "Plataforma ML Nissan"
    page.window_width = 900
    page.window_height = 700
    page.padding = 20
    page.scroll = "auto"
    # Inicializa Snackbar sin contenido
    page.snack_bar = ft.SnackBar(ft.Text(""), open=False)

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
            show_message(page, f"Error: {resp.text}")

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
    # Picker que invoca upload_file y luego recarga lista
    def on_file_result(e):
        upload_file(e, page, list_view, refresh_files)
    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    def refresh_files():
        list_view.controls.clear()
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/files/list", headers=headers)
        if resp.status_code == 200:
            for f in resp.json():
                list_view.controls.append(ft.ListTile(title=f['filename'], subtitle=f"ID: {f['id']}"))
        else:
            show_message(page, "Error al listar archivos")
        page.update()

    # Toolbar sin iconos para compatibilidad web
    toolbar = ft.Row([
        ft.ElevatedButton("Subir CSV", on_click=lambda e: file_picker.pick_files(allow_multiple=False)),
        ft.ElevatedButton("Refrescar lista", on_click=lambda e: refresh_files()),
    ])
    refresh_files()
    return ft.Column([toolbar, list_view], expand=1, spacing=10)


def upload_file(e, page: ft.Page, list_view: ft.ListView, refresh_fn):
    if e.files:
        file = e.files[0]
        # Leer datos ya sea desde path (desktop) o bytes (web)
        # Leer datos desde el sistema de archivos o desde memoria web
        try:
            if file.path:
                with open(file.path, "rb") as f:
                    file_bytes = f.read()
            else:
                file_bytes = file.read_bytes()
        except Exception:
            show_message(page, "Error leyendo el archivo")
            return
        buf = io.BytesIO(file_bytes)
        files_param = {"file": (file.name, buf, "text/csv")}
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(f"{BASE_URL}/files/upload", files=files_param, headers=headers)
        if resp.status_code == 201:
            show_message(page, "Archivo subido con éxito")
            # Recargar lista de archivos
            refresh_fn()
        else:
            show_message(page, "Error al subir archivo")
    else:
        show_message(page, "No se seleccionó ningún archivo", ft.colors.RED)


def preprocess_view(page: ft.Page):
    # Componentes de preprocesamiento
    file_dd = ft.Dropdown(label="Seleccionar archivo", width=300)
    remove_nulls = ft.Checkbox(label="Eliminar valores nulos", value=True)
    fill_nulls = ft.Checkbox(label="Rellenar valores nulos", value=False)
    fill_method = ft.Dropdown(
        label="Método relleno",
        options=[
            ft.dropdown.Option("mean", "mean"),
            ft.dropdown.Option("median", "median"),
            ft.dropdown.Option("mode", "mode"),
        ],
        value="mean",
        width=150,
    )
    drop_dups = ft.Checkbox(label="Eliminar duplicados", value=True)
    remove_outliers = ft.Checkbox(label="Eliminar outliers", value=False)
    result_panel = ft.Column(expand=1)

    def load_files():
        headers={"Authorization":f"Bearer {token}"}
        resp=requests.get(f"{BASE_URL}/files/list",headers=headers)
        if resp.status_code==200:
            file_dd.options=[ft.dropdown.Option(str(f['id']),f['filename']) for f in resp.json()]
            page.update()
        else:
            show_message(page,"Error cargando archivos")

    def clean_data(e):
        if not file_dd.value:
            show_message(page,"Seleccione un archivo")
            return
        payload={
            "remove_nulls":remove_nulls.value,
            "fill_nulls":fill_nulls.value,
            "fill_method":fill_method.value,
            "drop_duplicates":drop_dups.value,
            "remove_outliers":remove_outliers.value
        }
        headers={"Authorization":f"Bearer {token}"}
        resp=requests.post(f"{BASE_URL}/preprocessing/{file_dd.value}/clean",json=payload,headers=headers)
        if resp.status_code==200:
            stats=resp.json()
            # Mostrar preview
            records=stats.get('preview',[])
            cols=list(records[0].keys()) if records else []
            table=[ft.Row([ft.Text(str(r[c])) for c in cols]) for r in records]
            result_panel.controls=[ft.Text("Preview:"),ft.Column(table)]
        else:
            show_message(page,"Error en preprocesamiento")
        page.update()

    def analyze(e):
        if not file_dd.value:
            show_message(page,"Seleccione un archivo")
            return
        headers={"Authorization":f"Bearer {token}"}
        resp=requests.get(f"{BASE_URL}/preprocessing/{file_dd.value}/analysis",headers=headers)
        if resp.status_code==200:
            analysis=resp.json()
            result_panel.controls=[ft.Text(str(analysis))]
        else:
            show_message(page,"Error en análisis")
        page.update()

    load_files()
    toolbar=ft.Row([file_dd,remove_nulls,fill_nulls,fill_method,drop_dups,remove_outliers],spacing=10)
    buttons=ft.Row([ft.ElevatedButton("Limpiar",on_click=clean_data),ft.ElevatedButton("Analizar",on_click=analyze)],spacing=10)
    return ft.Column([toolbar,buttons,ft.Divider(),result_panel],expand=1,spacing=20)


def train_view(page: ft.Page):
    # Componentes de entrenamiento
    file_dd = ft.Dropdown(label="Archivo", width=300)
    model_dd = ft.Dropdown(
        label="Algoritmo",
        options=[
            ft.dropdown.Option("linear_regression", "linear_regression"),
            ft.dropdown.Option("svr", "svr"),
            ft.dropdown.Option("elasticnet", "elasticnet"),
            ft.dropdown.Option("sgd", "sgd"),
        ],
        value="linear_regression",
        width=200,
    )
    target = ft.TextField(label="Columna objetivo",width=200)
    features = ft.TextField(label="Columnas (coma)",width=300)
    result_txt = ft.Text("")

    def load_files():
        headers={"Authorization":f"Bearer {token}"}
        resp=requests.get(f"{BASE_URL}/files/list",headers=headers)
        if resp.status_code==200:
            file_dd.options=[ft.dropdown.Option(str(f['id']),f['filename']) for f in resp.json()]
            page.update()
        else:
            show_message(page,"Error cargando archivos")

    def train(e):
        if not file_dd.value or not target.value or not features.value:
            show_message(page,"Complete todos los campos")
            return
        cols=[c.strip() for c in features.value.split(',')]
        payload={"file_id":int(file_dd.value),"model_type":model_dd.value,"target_column":target.value,"feature_columns":cols}
        headers={"Authorization":f"Bearer {token}"}
        resp=requests.post(f"{BASE_URL}/models/train",json=payload,headers=headers)
        if resp.status_code==202:
            show_message(page,"Entrenamiento iniciado")
        else:
            show_message(page,"Error en entrenamiento")
        page.update()

    load_files()
    toolbar=ft.Row([file_dd,model_dd,target,features],spacing=10)
    return ft.Column([toolbar,ft.ElevatedButton("Entrenar",on_click=train),ft.Divider(),result_txt],expand=1,spacing=20)


def models_view(page: ft.Page):
    list_view=ft.ListView(expand=1,spacing=5)
    def refresh():
        headers={"Authorization":f"Bearer {token}"}
        resp=requests.get(f"{BASE_URL}/models/list",headers=headers)
        if resp.status_code==200:
            list_view.controls=[ft.ListTile(title=f"ID:{m['model_id']} - {m['model_type']}",
                on_click=lambda e,m=m: show_details(m['model_id'])) for m in resp.json()]
            page.update()
        else:
            show_message(page,"Error listando modelos")
    def show_details(mid:int):
        headers={"Authorization":f"Bearer {token}"}
        resp=requests.get(f"{BASE_URL}/models/{mid}",headers=headers)
        if resp.status_code==200:
            dlg=ft.AlertDialog(title=ft.Text("Detalles del Modelo"),content=ft.Text(str(resp.json())),actions=[ft.TextButton("Cerrar",on_click=lambda e: dlg.close())])
            page.dialog=dlg;dlg.open=True;page.update()
    def delete_model(mid:int):
        headers={"Authorization":f"Bearer {token}"}
        requests.delete(f"{BASE_URL}/models/{mid}",headers=headers)
        refresh()

    toolbar=ft.Row([ft.ElevatedButton("Refrescar",on_click=lambda e: refresh())],spacing=10)
    refresh()
    return ft.Column([toolbar,list_view],expand=1,spacing=10)


def predict_view(page: ft.Page):
    model_dd=ft.Dropdown(label="Modelo",width=300)
    features=ft.TextField(label="Valores (coma)",width=400)
    result_txt=ft.Text("")
    def load_models():
        headers={"Authorization":f"Bearer {token}"}
        resp=requests.get(f"{BASE_URL}/models/list",headers=headers)
        if resp.status_code==200:
            model_dd.options=[ft.dropdown.Option(str(m['model_id']),str(m['model_id'])) for m in resp.json()]
            page.update()
        else:
            show_message(page,"Error cargando modelos")
    def predict(e):
        if not model_dd.value or not features.value:
            show_message(page,"Seleccione modelo e ingrese valores")
            return
        vals=[float(v) for v in features.value.split(',')]
        headers={"Authorization":f"Bearer {token}"}
        resp=requests.post(f"{BASE_URL}/models/{model_dd.value}/predict",json={"features":vals},headers=headers)
        if resp.status_code==200:
            result_txt.value=str(resp.json())
        else:
            show_message(page,"Error en predicción")
        page.update()

    load_models()
    return ft.Column([ft.Row([model_dd,features]),ft.ElevatedButton("Predecir",on_click=predict),ft.Divider(),result_txt],expand=1,spacing=20)


if __name__ == "__main__":
    # Ejecutar en modo web en puerto 8501
    ft.app(target=main, view=ft.WEB_BROWSER, port=8501)