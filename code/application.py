import requests
import base64
import json
from flask import Flask, render_template, request
from translate import Translator
import textwrap
import jinja2
import socket
import dns.resolver
import boto3
import socket
import sys
# from mcstatus.server import MinecraftServer
from flask import redirect




application = Flask(__name__)

s3_client = boto3.client('s3')
bucket_name = 'a3-share'

API_GATEWAY_ENDPOINT = 'https://isi9we827f.execute-api.us-east-1.amazonaws.com/Beta'

def get_nav(page_name):
    if page_name == "Player Lookup":
        nav_icon_paths = [
        'image/nav-sel_player_lookup.png',
        'image/nav_server_information.png',
        'image/nav_translate.png',
        'image/nav_block_information.png',
        'image/nav_book.png',
        'image/nav_networking.png'
        ]
        return nav_icon_paths
    if page_name == "Lookup Server by IP":
        nav_icon_paths = [
        'image/nav_player_lookup.png',
        'image/nav-sel_server_information.png',
        'image/nav_translate.png',
        'image/nav_block_information.png',
        'image/nav_book.png',
        'image/nav_networking.png'
        ]
        return nav_icon_paths
    if page_name == "Localization Tools":
        nav_icon_paths = [
        'image/nav_player_lookup.png',
        'image/nav_server_information.png',
        'image/nav-sel_translate.png',
        'image/nav_block_information.png',
        'image/nav_book.png',
        'image/nav_networking.png'
        ]
        return nav_icon_paths
    if page_name == "Find Block Information":
        nav_icon_paths = [
        'image/nav_player_lookup.png',
        'image/nav_server_information.png',
        'image/nav_translate.png',
        'image/nav-sel_block_information.png',
        'image/nav_book.png',
        'image/nav_networking.png'
        ]
        return nav_icon_paths
    if page_name == "Format Book JSON Text":
        nav_icon_paths = [
        'image/nav_player_lookup.png',
        'image/nav_server_information.png',
        'image/nav_translate.png',
        'image/nav_block_information.png',
        'image/nav-sel_book.png',
        'image/nav_networking.png'
        ]
        return nav_icon_paths
    if page_name == "Share":
        nav_icon_paths = [
        'image/nav_player_lookup.png',
        'image/nav_server_information.png',
        'image/nav_translate.png',
        'image/nav_block_information.png',
        'image/nav_book.png',
        'image/nav-sel_networking.png'
        ]
        return nav_icon_paths
    nav_icon_paths = [
    'image/nav_player_lookup.png',
    'image/nav_server_information.png',
    'image/nav_translate.png',
    'image/nav_block_information.png',
    'image/nav_book.png',
    'image/nav_networking.png'
    ]
    return nav_icon_paths
    
@application.template_filter('b64decode')
def base64_decode(value):
    return base64.b64decode(value).decode('utf-8')

@application.template_filter('from_json')
def from_json(value):
    return json.loads(value)

@application.route('/')
def home():
    return player_lookup()


@application.route('/player_lookup', methods=['GET', 'POST'])
def player_lookup():
    page_name = "Player Lookup"
    nav_icon_paths = get_nav(page_name)
    if request.method == 'POST':
        player_name = request.form['player_name']

        # Step 1: Get player UUID from username
        username_api_url = f'https://api.mojang.com/users/profiles/minecraft/{player_name}'
        username_response = requests.get(username_api_url)
        if username_response.status_code == 200:
            username_data = username_response.json()
            player_uuid = username_data['id']

            # Step 2: Get player profile using UUID
            profile_api_url = f'https://sessionserver.mojang.com/session/minecraft/profile/{player_uuid}'
            profile_response = requests.get(profile_api_url)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()

                return render_template('player_lookup.html', nav_icon_paths=nav_icon_paths, page_name=page_name, player_data=profile_data)

        return render_template('player_lookup.html', nav_icon_paths=nav_icon_paths, page_name=page_name, error='Player not found')

    return render_template('player_lookup.html', nav_icon_paths=nav_icon_paths, page_name=page_name)



def mc_server_ping(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        
        request_data = b'\x00\x00' + bytearray([len(host)]) + host.encode('utf-8') + bytearray([port >> 8, port & 0xFF]) + b'\x01'
        sock.send(request_data)
        
        response_data = sock.recv(4096)
        
        sock.close()
        
        response = response_data.decode('utf-8', errors='replace')
        
        response = json.loads(response)
        
        if 'description' not in response:
            response['description'] = {'text': 'No MOTD available.'}
        
        return response
    except socket.timeout:
        return None
    except ConnectionRefusedError:
        return None
    except json.JSONDecodeError:
        return None


@application.route('/server_lookup', methods=['GET', 'POST'])
def server_status():
    page_name = "Lookup Server by IP"
    nav_icon_paths = get_nav(page_name)
    error_message = "Server is offline or unreachable."
    if request.method == 'POST':
        server_address = request.form['server_address']
        server_port = int(request.form.get('server_port', '25565'))

        try:
            response = mc_server_ping(server_address, server_port)
            if response is None:  
                return render_template('server_lookup.html', error_message=error_message, nav_icon_paths=nav_icon_paths, page_name=page_name)
            else:
                return render_template('server_lookup.html', response=response, nav_icon_paths=nav_icon_paths, page_name=page_name)
        except Exception as e:
            return render_template('server_lookup.html', error_message=error_message, nav_icon_paths=nav_icon_paths, page_name=page_name)

    return render_template('server_lookup.html', nav_icon_paths=nav_icon_paths, page_name=page_name)

    

def format_block_information(response):
    item = response['body']  # Extract the 'body' dictionary from the response

    title = item.get('title_f', '')  # Get the 'title_f' value, defaulting to an empty string if not present
    description = item.get('summary', '')  # Get the 'summary' value, defaulting to an empty string if not present
    url = item.get('url', '')  # Get the 'url' value, defaulting to an empty string if not present
    image_url = item.get('image', '')  # Get the 'image' value, defaulting to an empty string if not present
    # image_url = image_url.replace('https://', 'http://')
    
    display_type = get_display_type(image_url)
    image_url = remove_revision_text(image_url)

    formatted_result = {
        'title_f': title,
        'summary': description,
        'url': url,
        'image': image_url,
        'display_type': display_type
    }

    print (formatted_result)
    return [formatted_result]

def format_block_search_information(response):
    try:
        item = response['body']
        title = item.get('title_f', '')
        description = item.get('summary', '')
        url = item.get('url', '')
        image_url = item.get('image', '')
        # image_url = image_url.replace('https://', 'http://')

        display_type = get_display_type(image_url)
        image_url = remove_revision_text(image_url)

        formatted_result = {
            'title_f': title,
            'summary': description,
            'url': url,
            'image': image_url,
            'display_type': display_type
        }

        return [formatted_result]
    except Exception as e:
        # Handle the case when no matching items are found or response is not in the expected format
        return None



def get_display_type(image_url):
    if image_url is None:
        return 'unknown'

    # Find the extension just before "/revision/"
    extension_start = image_url.rfind('.', 0, image_url.rfind('/revision/'))
    extension_end = image_url.rfind('/revision/')
    
    if extension_start == -1 or extension_end == -1 or extension_end <= extension_start:
        return 'unknown'

    file_extension = image_url[extension_start + 1 : extension_end].lower()

    if file_extension in ['png', 'jpeg', 'jpg', 'gif', 'webp']:
        return 'image'
    elif file_extension in ['mp3', 'ogg', 'wav']:
        return 'audio'
    elif file_extension in ['mp4', 'mov', 'avi', 'wmv']:
        return 'video'
    else:
        return 'unknown'


def remove_revision_text(image_url):
    revision_index = image_url.find('/revision/')
    if revision_index != -1:
        image_url = image_url[:revision_index]
    return image_url


@application.route('/block_information', methods=['GET', 'POST'])
def block_information():
    page_name = "Find Block Information"
    nav_icon_paths = get_nav(page_name)

    if request.method == 'POST':
        if 'random' in request.form:
            # Make a GET request to the API Gateway endpoint for random-item
            response = requests.get(f'{API_GATEWAY_ENDPOINT}/random-item')

            print (response.json())
            if response.status_code == 200:
                random_item = response.json()

                jinja_formatted_response = format_block_information(random_item)

                return render_template('block_information.html', nav_icon_paths=nav_icon_paths, page_name=page_name, search_results=jinja_formatted_response)

            else:
                return render_template('block_information.html', nav_icon_paths=nav_icon_paths, page_name=page_name, search_results=None)

        elif 'search' in request.form:
            error_message = "there was nothing that could be found.."
            search_query = request.form.get('search_query')

            # Make a POST request to the API Gateway endpoint for block-information
            response = requests.post(f'{API_GATEWAY_ENDPOINT}/block-information', json={'search_query': search_query})

            if response.status_code == 200:
                search_results = response.json()
                print (search_results)

                jinja_formatted_responce = format_block_search_information(search_results)

                if jinja_formatted_responce is not None:
                    return render_template('block_information.html', nav_icon_paths=nav_icon_paths, page_name=page_name, search_results=jinja_formatted_responce)
                else:
                    return render_template('block_information.html', nav_icon_paths=nav_icon_paths, page_name=page_name, error_message=error_message)
            elif response.status_code == 400:
                return render_template('block_information.html', nav_icon_paths=nav_icon_paths, page_name=page_name, error_message=error_message)
            else:
                return render_template('block_information.html', nav_icon_paths=nav_icon_paths, page_name=page_name, error_message=error_message)

    
    return render_template('block_information.html', nav_icon_paths=nav_icon_paths, page_name=page_name)


@application.route('/translate', methods=['GET', 'POST'])
def translate():
    page_name = "Localization Tools"
    nav_icon_paths = get_nav(page_name)

    if request.method == 'POST':
        text = request.form['text']
        source_language = request.form['source_language']
        target_language = request.form['target_language']

        translator = Translator(from_lang=source_language, to_lang=target_language)
        translation = translator.translate(text)

        return render_template('translate.html', nav_icon_paths=nav_icon_paths, page_name=page_name, translation=translation, input_text=text)

    return render_template('translate.html', nav_icon_paths=nav_icon_paths, page_name=page_name)


@application.route('/send_to_book_formatter', methods=['POST'])
def send_to_book_formatter():
    page_name = "Format Book JSON Text"
    nav_icon_paths = get_nav(page_name)
    translation = request.form['translation']

    return render_template('book_formatter.html', nav_icon_paths=nav_icon_paths, page_name=page_name, translation=translation)


@application.route('/book_formatter', methods=['GET', 'POST'])
def book_formatter():
    page_name = "Format Book JSON Text"
    nav_icon_paths = get_nav(page_name)

    if request.method == 'POST':
        try:
            text = request.form['book_text']
            title = request.form['title']
        except Exception as e:
            print(f"Error occurred: {e}")

        # Process the text and replace new lines with '\n'
        processed_text = text.replace('\n', '\\\\n')
        processed_text = text.replace('\n', '\\\\n')
        limited_text = textwrap.fill(processed_text, width=35)


        # Check if the 'color' field exists in the form data
        if 'color' in request.form:
            color = request.form['color']
            if color == "":
                color = "black"
        else:
            color = 'black'  # Set a default color if not provided

        # Construct the book text
        book_text = f'/give @p written_book{{pages:[\'{{"text":"{limited_text}","color":"{color}"}}\'], title:"{title}", author:"MineDev"}}'

        return render_template('book_formatter.html', book_text=book_text, nav_icon_paths=nav_icon_paths, page_name=page_name)

    # If it's a GET request, render the template without the book_text
    return render_template('book_formatter.html', nav_icon_paths=nav_icon_paths, page_name=page_name)



@application.route('/networking', methods=['GET', 'POST'])
def networking():
    if request.method == 'POST':
        # Handle the file upload here
        file = request.files['file']
        picture = request.files['picture']
        
        # Save the uploaded files to S3
        s3_client = boto3.client('s3')
        if file:
            file_key = f"share/file/{file.filename}"
            s3_client.upload_fileobj(file, bucket_name, file_key)
        if picture:
            image_key = f"share/image/{picture.filename}"
            s3_client.upload_fileobj(picture, bucket_name, image_key)
        
        # Return a response or redirect as needed
        return redirect('/networking')  # Redirect to GET request to display the updated content
        
    else:  # GET method
        page_name = "Share"
        nav_icon_paths = get_nav(page_name)

        s3_client = boto3.client('s3')

        # Fetch image objects from S3
        response_images = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='share/image/')
        image_objects = response_images.get('Contents', [])

        # Fetch file objects from S3
        response_files = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='share/file/')
        file_objects = response_files.get('Contents', [])

        image_file_pairs = []

        for image_obj in image_objects:
            image_key = image_obj['Key']
            file_key = f"share/file/{image_key.split('/')[-1]}"
            file_obj = next((obj for obj in file_objects if obj['Key'] == file_key), None)

            if file_obj:
                image_url = f"https://{bucket_name}.s3.amazonaws.com/{image_key}"
                file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
                image_file_pairs.append((image_url, file_url))

        return render_template('networking.html', nav_icon_paths=nav_icon_paths, page_name=page_name,
                               image_file_pairs=image_file_pairs)





if __name__ == '__main__':
    application.debug = True
    application.run()