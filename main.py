from pydoc import text
from unittest.mock import PropertyMock
import feedparser
import re
import os
import json
import urllib.parse
from pyrogram import Client, filters
from urllib.parse import quote_plus
from pyrogram.types import Message,InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import requests
import asyncio
from bs4 import BeautifulSoup
from typing import List
from json.decoder import JSONDecodeError


bot_token = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

# Crea una nueva instancia de Pyrogram
app = Client("VIGITEC", bot_token= bot_token)

#Canal de envio
primary_channel = -1001887984798

# Lista de suscripciones
subscriptions = []

# Lista de comandos deshabilitados
comandos_deshabilitados = []

# Reemplazar con los ids autorizados a usar el bot
ids_autorizados = [1154130101,1282049429,1647438450,1548594902,5333140126,833307726,974053304,2143707986,1109313691]
canal_notificaciones = -1001887984798
mensaje_notificacion_enviado = False
id_admin = 1154130101



###################################
#Funcion que inicia el BOT
###################################

@app.on_message(filters.command("start"))
def start(client, message):
    global mensaje_notificacion_enviado
    if message.from_user.id not in ids_autorizados:
        message.reply_text("Lo siento, no estás autorizado para usar este bot.")
        if not mensaje_notificacion_enviado:
            client.send_message(canal_notificaciones, f"El usuario @{message.from_user.username} con id {message.from_user.id} intentó utilizar el bot sin autorización.")
            mensaje_notificacion_enviado = True
            
    if comando_deshabilitado("start"):
        client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
        user = message.from_user.username
        # Envía un mensaje de bienvenida
        message.reply_text(f"¡Hola {user}! ¡Bienvenido a mi bot de Telegram!\nSoy un bot creado por @JNovaM que tiene diferentes funciones para búsqueda de noticias o información de artículos científicos.\nPara saber más de como usarme utilice el comando /help")
        mensaje_notificacion_enviado = False



###################################
#Funcion que ejecuta el comando /help
###################################

# Define el comando /help
@app.on_message(filters.command("help"))
def start(client, message):
    if message.from_user.id not in ids_autorizados:
        message.reply_text("Lo siento, no estás autorizado para usar este bot.")
    
    if comando_deshabilitado("help"):
        client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
     user = message.from_user.username
     # Envía un mensaje de bienvenida
     message.reply_text(f"Estos son los comandos que puedes usar en el bot:\n/subscribe - Permite suscribirse a un RSS o Feed\n/unsubscribe - Elimina la subscripción indicando el número de la misma\n/list - Muestra la lista de suscripciones\n/check - Muestra las últimas actualizaciones, lo hace automático cada 5 minutos\n/doaj - Busca en el sitio de DOAJ\n/news - Busca noticias en BING\n/google - Busca en Google Schoolar\n/buscar - Busca en Google https://www.google.com\n/duck - Busca en DuckDuck pero devuelve los enlaces de la búsqueda\n/lib1 - Busca nombre de libros y sus autores en openlibrary.org\n/lib2 - Busca libros y sus autores en openlibra.comn")

 

###################################
#Funcion para habilitar/deshabilitar comandos para mantenimiento
###################################

 # Comando para deshabilitar un comando
@app.on_message(filters.command("des") & filters.user(id_admin))
def deshabilitar_comando(client, message):
    comando = message.text.split(" ", maxsplit=1)[1].lower()

    if comando in comandos_deshabilitados:
        client.send_message(message.chat.id, f"El comando /{comando} ya está deshabilitado.")
    else:
        comandos_deshabilitados.append(comando)
        client.send_message(message.chat.id, f"El comando /{comando} ha sido deshabilitado correctamente.")

# Comando para habilitar un comando
@app.on_message(filters.command("hab") & filters.user(id_admin))
def habilitar_comando(client, message):
    comando = message.text.split(" ", maxsplit=1)[1].lower()

    if comando in comandos_deshabilitados:
        comandos_deshabilitados.remove(comando)
        client.send_message(message.chat.id, f"El comando /{comando} ha sido habilitado correctamente.")
    else:
        client.send_message(message.chat.id, f"El comando /{comando} no está deshabilitado.")

# Verificar si un comando está deshabilitado
def comando_deshabilitado(comando):
    comando = comando.lower()
    return comando in comandos_deshabilitados
    


###################################
#Funcion para subscribirse a un RSS
###################################

# Función para suscribirse a un feed RSS
async def subscribe_to_feed(url: str, chat_id: int):
    # Descarga el feed RSS
    feed = feedparser.parse(url)

    # Envía los últimos 10 artículos al chat especificado
    for entry in feed.entries[:10]: #Aqui se cambia el numero de articulos que queremos que envie
        message = f"🖥(R): <b>{entry.title}</b>\n\nResumen: {entry.summary}\n\n<a href='{entry.link}'>Link al artículo</a>"
        await app.send_message(primary_channel, message, disable_web_page_preview=True)

    # Genera un número único para la suscripción y la agrega a la lista de suscripciones
    subscription_number = len(subscriptions) + 1
    subscriptions.append({"number": subscription_number, "url": url, "chat_id": chat_id})

    # Envía un mensaje de confirmación con el número de la suscripción
    await app.send_message(chat_id, f"Suscripción exitosa. Número de suscripción: {subscription_number}")

    # Función para cancelar la suscripción a un feed RSS

# Manejador de comandos para suscribirse
@app.on_message(filters.command("subscribe"))
async def subscribe_command_handler(client: Client, message: Message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
        
    if comando_deshabilitado("subscribe"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    # Obtén el URL del feed RSS del mensaje
    else:
     url = message.text.split(" ", 1)[1]

    # Suscríbete al feed RSS y envía los últimos artículos al chat
     await subscribe_to_feed(url, message.chat.id)



###################################
#Funcion para mostrar la lista de subscripciones
###################################

# Manejador de comandos para listar las suscripciones
@app.on_message(filters.command("list"))
async def list_command_handler(client: Client, message: Message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
    
    if comando_deshabilitado("list"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
    # Crea una lista con los números y URLs de los feeds suscritos
     subscriptions_list = [f"{subscription['number']}. {subscription['url']}" for subscription in subscriptions]

    # Si no hay suscripciones, envía un mensaje indicándolo
    if not subscriptions_list:
        await message.reply_text("No estás suscrito a ningún feed.")
        return

    # Envía un mensaje con los números y URLs de los feeds suscritos
    message_text = "<b>Feeds suscritos:</b>\n\n"
    for subscription in subscriptions_list:
        message_text += f"{subscription}\n\n"
    await message.reply_text(message_text, disable_web_page_preview=True)



###################################
#Funcion para eliminar la subscripcion a un RSS
###################################

# Función para eliminar una suscripción según el número
async def unsubscribe(subscription_number: int, chat_id: int):
    # Busca la suscripción correspondiente al número y al chat especificados
    for subscription in subscriptions:
        if subscription["number"] == subscription_number and subscription["chat_id"] == chat_id:
            subscriptions.remove(subscription)
            message = f"Se ha eliminado la suscripción {subscription_number}."
            await app.send_message(chat_id, message)
            return

    # Si no se encuentra la suscripción, envía un mensaje indicándolo
    message = f"No se encontró la suscripción {subscription_number}."
    await app.send_message(chat_id, message)


# Manejador de comandos para eliminar una suscripción
@app.on_message(filters.command("unsubscribe"))
async def unsubscribe_command_handler(client: Client, message: Message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
    
    if comando_deshabilitado("unsubscribe"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
               
    # Obtiene el número de la suscripción del mensaje
     try:
        subscription_number = int(message.text.split(" ", 1)[1])
     except (IndexError, ValueError):
        await message.reply_text("Uso: /unsubscribe <número de suscripción>")
        return

    # Elimina la suscripción y envía un mensaje de confirmación
     await unsubscribe(subscription_number, message.chat.id)



###################################
#Funcion para realizar actualizaciones de los nuevos mensajes
###################################

async def check_updates():
    await check_feed_task()  # Llamada a la función que verifica las actualizaciones
    # Envía un mensaje al chat indicando que se han verificado las actualizaciones


@app.on_message(filters.command("check"))
async def check_command_handler(client, message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
    
    if comando_deshabilitado("check"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
    # Llama a la función que verifica las actualizaciones y envía un mensaje de confirmación
     await check_updates()

# Tarea de fondo para comprobar nuevos artículos en el feed RSS

async def check_feed_task():
    while True:
        # Verifica cada una de las suscripciones
        for subscription in subscriptions:
            url = subscription["url"]
            chat_id = subscription["chat_id"]

            # Descarga el feed RSS
            feed = feedparser.parse(url)

            # Comprueba si hay nuevos artículos
            if feed.entries:
                # Si es el primer chequeo, envía los últimos 10 artículos
                if "last_entry" not in subscription:
                    for entry in feed.entries[:10]: #Aqui se cambia el numero de articulos que queremos que envie
                        message = f"🖥(R): <b>{entry.title}</b>\n\n{entry.summary}\n\n<a href='{entry.link}'>Link al artículo</a>"
                        await app.send_message(primary_channel, message, disable_web_page_preview=True)
                # Si hay nuevos artículos, envía solo los que no se han visto antes
                else:
                    last_entry = subscription["last_entry"]
                    new_entries = [entry for entry in feed.entries if
                                   entry.published_parsed > last_entry.published_parsed]
                    for entry in new_entries:
                        message = f"<b>{entry.title}</b>\n\n{entry.summary}\n\n<a href='{entry.link}'>Link al artículo</a>"
                        await app.send_message(primary_channel, message, disable_web_page_preview=True)

                # Actualiza el último artículo visto
                subscription["last_entry"] = feed.entries[0]

                message = "Se han verificado las últimas actualizaciones y han sido enviadas al."
                await app.send_message(chat_id, message)

        # Espera 5 minutos antes de volver a revisar
        await asyncio.sleep(300)

###################################
# Funcion para hacer busquedas en DOAJ (Directorio de revistas de acceso abierto)
###################################

@app.on_message(filters.command("doaj"))
async def search_command_handler(client: Client, message: Message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
        return
    
    if comando_deshabilitado("doaj"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
     try:
      query = message.text.split(" ", 1)[1]
      response = requests.get(f"https://www.doaj.org/api/v3/search/{query}").json()
      if "total" in response and response["total"] > 0:
        await message.reply_text("Se enviaron los articulos al canal. ")
        for i in range(min(5, response["total"])):
            await message.reply_text("Se enviaron los artículos al canal.")
            for i in range(min(5, response["total"])):
                result = response["results"][i]
                title = result["bibjson"]["title"]
                authors = result["bibjson"].get("author", [])
                year = result["bibjson"]["year"]
                url = result["bibjson"].get("link", [{"url": ""}])[0]["url"]
                summary_html = result["bibjson"].get("abstract", "")
                summary = BeautifulSoup(summary_html, "html.parser").get_text().strip()
                author_str = "\n".join([author.get("name", "") for author in authors])
                message_text = f"🖥(A): {title}\n\nResumen: {summary}\n\nAutores: {author_str}\n\nAño: {year}\n\nLink: {url}"
                await app.send_message(primary_channel, message_text)
        else:
            await message.reply("No se encontraron resultados para la búsqueda especificada.")
     except IndexError:
        await message.reply("Por favor proporcione una consulta de búsqueda válida después del comando /doaj.")
        


# Función para realizar la búsqueda en el feed RSS de DOAJ
def perform_rss_search(query):
    url = f"https://doaj.org/feed?query={query}"

    feed = feedparser.parse(url)

    return feed.entries

# Función para enviar los resultados de búsqueda en un mensaje de Telegram
async def send_search_results(message, results):
    if len(results) == 0:
        await message.reply_text("No se encontraron resultados para la búsqueda especificada.")
    else:
        mensaje = "Resultados de la búsqueda:\n"
        for i, result in enumerate(results, start=1):
            title = result.title
            link = result.link
            mensaje += f"{i}. {title}\n{link}\n\n"
            if i >= 10:  # Limita el número de resultados a mostrar
                break
        await message.reply_text(mensaje, disable_web_page_preview=True)

# Define la función para buscar en el feed RSS de DOAJ y mostrar los resultados
@app.on_message(filters.command("doaj_search"))
async def doaj_search(client, message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
    
    if comando_deshabilitado("doaj_search"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    else:
    query = " ".join(message.text.split(" ")[1:])

    try:
        search_results = perform_rss_search(query)
        await send_search_results(message, search_results)
    except Exception as e:
        await message.reply_text("Ocurrió un error al realizar la búsqueda. Por favor, inténtalo de nuevo más tarde.")


###################################
# Funcion para hacer busquedas de noticias nuevas RSS en BING
###################################


def get_news_rss(query: str, num_results: int = 5) -> List[str]:
    query_encoded = quote_plus(query)
    url = f"https://www.bing.com/news/search?q={query_encoded}&format=rss"
    feed = feedparser.parse(url)

    results = []
    for i, entry in enumerate(feed.entries):
        if i == num_results:
            break
        results.append((entry.title, entry.summary, entry.link))
    return results


def get_news_rss_from_html(html: str, num_results: int = 5) -> List[str]:
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    results = []
    for i, link in enumerate(links):
        if i == num_results:
            break
        if 'href' in link.attrs:
            url = link.attrs['href']
            if url.startswith('http'):
                results.append(url)
    return results


@app.on_message(filters.command("news"))
async def news(client: Client, message: Message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
    
    if comando_deshabilitado("news"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
     if len(message.text.split()) > 1:
       query = " ".join(message.text.split(" ")[1:])
     else:
        await message.reply_text("Por favor proporcione una consulta de búsqueda válida después del comando /news.")
        return

     headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
     }

     url = f"https://www.bing.com/news/search?q={query}"
     response = requests.get(url, headers=headers)
     rss_links = get_news_rss_from_html(response.text)

     if not rss_links:
        rss_links = get_news_rss(query)

     if not rss_links:
        await message.reply_text(f"No se encontraron noticias para la búsqueda '{query}'.")
        return

     await message.reply_text(f"Los resultados fueron enviados al canal. '{query}'")

     for title, summary, link in rss_links:
       await app.send_message(primary_channel,f"🖥(N):{title}\n\nResumen:{summary}\n\n<a href='{link}'>Link al artículo</a>", disable_web_page_preview=True)



###################################
#Funcion para busquedas de libros en el sitio openlibrary.org (https://openlibrary.org/developers/api)
###################################

def open_library_search(query):
    url = f"https://openlibrary.org/search.json?q={query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "docs" in data:
            results = data["docs"]
            return results
    except requests.exceptions.RequestException as e:
        print("Error en la solicitud:", e)
    
    return None


@app.on_message(filters.command("lib1"))
async def lib_search(client, message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
    
    if comando_deshabilitado("lib1"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
     query = " ".join(message.command[1:])
     if not query:
        await message.reply_text("Por favor proporciona una consulta de búsqueda después del comando /lib1.")
        return
    
     results = open_library_search(query)
    
     if results:
        response = "Resultados de la búsqueda:\n\n"
        count = 0
        for result in results:
            if count == 5:
                break
            
            title = result.get("title", "")
            author = result.get("author_name", [])
            year = result.get("first_publish_year", "")
            link = result.get("key", "")
            
            response += f"🖥(L): {title}\nAutor: {', '.join(author)}\nAño: {year}\n\n"
            count += 1
    
     else:
        response = "No se encontraron resultados para la búsqueda."
    
     await client.send_message(message.chat.id, response)



###################################
#Funcion para busquedas de libros en el sitio OpenLibra (https://openlibra.com/es/page/public-api)
###################################

@app.on_message(filters.command("lib2"))
async def guia_search(client, message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
    
    if comando_deshabilitado("lib2"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
     query = " ".join(message.command[1:])
     if not query:
        await message.reply_text("Por favor proporciona una consulta de búsqueda después del comando /lib2.")
        return

     results = perform_guia_search(query)

     if results:
        count = 0
        for result in results:
            if count >= 5:
                break
            title = result.get("title", "")
            author = result.get("author", "")
            categories = result.get("categories", [])
            url_details = result.get("url_details", "")
            url_download = result.get("url_download", "")

            category_names = [category["name"] for category in categories] if categories else []
            categories_str = ", ".join(category_names) if category_names else "N/A"

            response = f"🖥(L): {title}\nAutor: {author}\nCategoría: {categories_str}\nEnlace: {url_details}\nEnlace de descarga: {url_download}"
            await client.send_message(message.chat.id, response)
            count += 1
     else:
        response = "No se encontraron resultados para la búsqueda."
        await client.send_message(message.chat.id, response)


def perform_guia_search(query):
    query_encoded = quote_plus(query)
    url = f"https://www.etnassoft.com/api/v1/get/?keyword={query_encoded}"
    response = requests.get(url)
    data = response.json()
    results = []

    for item in data:
        title = item.get("title", "")
        author = item.get("author", "")
        categories = item.get("categories", [])
        url_details = item.get("url_details", "")
        url_download = item.get("url_download", "")

        result = {
            "title": title,
            "author": author,
            "categories": categories,
            "url_details": url_details,
            "url_download": url_download
        }

        results.append(result)

    return results



###################################
#Funcion para busquedas en Google Schoolar https://scholar.google.com/
###################################

# Comando para buscar en Google Scholar
@app.on_message(filters.command("google"))
async def buscar_en_google(client, message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
    
    if comando_deshabilitado("google"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
     query = " ".join(message.text.split(" ")[1:])
     if not query:
        await client.send_message(message.chat.id, "Por favor proporciona una consulta de búsqueda después del comando /google.")
        return

     results = buscar_en_google_scholar(query)

     if results:
        response = "🖥(SC):Resultados de la búsqueda en Google Scholar:\n\n"
        for result in results:
            title = result["title"]
            link = result["link"]
            summary = result["summary"]
            response += f"📚 Título: {title}\nℹ Resumen: {summary}\n🔗 <a href='{link}'>Link al artículo</a>\n\n"
        await client.send_message(message.chat.id, response,disable_web_page_preview=True)
     else:
        await client.send_message(message.chat.id, "No se encontraron resultados para la búsqueda en Google Scholar.")


# Función para buscar en Google Scholar
def buscar_en_google_scholar(query):
    url = f"https://scholar.google.com/scholar?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for result in soup.find_all("div", class_="gs_ri"):
        title_element = result.find("h3", class_="gs_rt")
        title = title_element.text if title_element else ""
        link = result.find("a")["href"]
        summary_element = result.find("div", class_="gs_rs")
        summary = summary_element.text if summary_element else ""

        # Limpiar el título
        cleaned_title = re.sub(r"\[.*?\]", "", title).strip()

        if cleaned_title and link:
            results.append({"title": cleaned_title, "link": link, "summary": summary})

    return results



###################################
#Funcion para busquedas en Google Schoolar https://google.com/
###################################

# Función para realizar la búsqueda en Google utilizando la API
def perform_google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    results = []
    if "items" in data:
        for item in data["items"]:
            title = item.get("title", "")
            link = item.get("link", "")
            summary = item.get("snippet", "")
            results.append({"title": title, "link": link, "summary": summary})

    return results

# Define la función para buscar en Google y mostrar los resultados
@app.on_message(filters.command("buscar"))
async def google_search(client, message):
    if message.from_user.id not in ids_autorizados:
        await message.reply_text("Lo siento, no estás autorizado para usar este bot.")
        return

    if comando_deshabilitado("buscar"):
        await client.send_message(message.chat.id, "Lo siento, este comando está deshabilitado por mantenimiento.")
        return
    
    else:
        query = " ".join(message.text.split(" ")[1:])
        if not query:
            await message.reply_text("Por favor proporciona una consulta de búsqueda después del comando /buscar.")
            return

        try:
            search_results = perform_google_search(query)

            if len(search_results) == 0:
                await message.reply_text(f"No se encontraron resultados para la búsqueda '{query}'.")
            else:
                mensaje = f"🖥(G):Resultados de la búsqueda '{query}':\n"
                for i, result in enumerate(search_results, start=1):
                    title = result["title"]
                    link = result["link"]
                    summary = result["summary"]
                    mensaje += f"{i}. {title}\n{link}\n{summary}\n\n"
                    if i >= 10:
                        break
                await message.reply_text(mensaje, disable_web_page_preview=True)

        except requests.exceptions.HTTPError as e:
            await message.reply_text("Se produjo un error al realizar la búsqueda. Por favor, inténtalo de nuevo más tarde.")

app.run()
