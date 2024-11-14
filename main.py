import requests
import random
from PIL import Image, ImageOps
from colorama import Fore, Style, init

# init colorama library
init()

# ASCII characters in increasing brightness
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

RESPONSE = None
DATA = None
NAME = None
TYPES = None
GEN_NAME = None

CENTERING_SIZE = 30

GEN_DATES = {
    "generation-i": 1996,
    "generation-ii": 1999,
    "generation-iii": 2002,
    "generation-iv": 2006,
    "generation-v": 2010,
    "generation-vi": 2013,
    "generation-vii": 2016,
    "generation-viii": 2019,
    "generation-ix": 2022,
}

CORRECT = False

def invert_image(image):
    # Inverts the colors (white becomes black and vice versa)
    return ImageOps.invert(image)

def collect_urls(data):
    urls = []
    if isinstance(data, dict):

        for key, value in data.items():

            if isinstance(value, dict):
                # recursividade
                urls.extend(collect_urls(value))

            elif isinstance(value, str) and value.startswith("http"):
                # adiciona no fim do trem
                urls.append(value)

    return urls

def rng_sprite(data):
    sprite_link = random.choice(list(data))

    print(sprite_link)

    return sprite_link    

def download_image(url, save_path):
    response = requests.get(url)

    if response.status_code == 200:

        with open(save_path, "wb") as file:

            file.write(response.content)

    else:
        print("Falha no download")

def resize_image(image, new_width=100):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(new_width * aspect_ratio * 0.5)  # Adjust for ASCII text aspect
    return image.resize((new_width, new_height))

def grayscale_image(image):
    return image.convert("L")  # Convert to grayscale

def map_pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = "".join(ASCII_CHARS[pixel // 25] for pixel in pixels)  # Map pixels to ASCII
    return ascii_str

def convert_image_to_ascii(image_path, new_width=100):
    image = Image.open(image_path)
    image = resize_image(image, new_width)
    image = grayscale_image(image)
    image = invert_image(image)
    ascii_str = map_pixels_to_ascii(image)

    # Format ASCII string into image dimensions
    width, _ = image.size
    ascii_img = "\n".join(ascii_str[i:i+width] for i in range(0, len(ascii_str), width))
    return ascii_img

def drawn_pokemon():
    global DATA
    
    # salva a imagem do pokemon
    download_image(rng_sprite(collect_urls(DATA['sprites'])), 'sprite.png')


    # desenha
    image_path = "sprite.png"
    ascii_art = convert_image_to_ascii(image_path)
    print(ascii_art)

def get_gen(species_url):
    # Fetch the species data
    species_response = requests.get(species_url)
    
    if species_response.status_code == 200:
        species_data = species_response.json()
        
        # Get the generation info from the species data
        return species_data["generation"]["name"]

def print_stats(pokemon_name):
    global CENTERING_SIZE, NAME, DATA, TYPES, GEN_DATES, CORRECT

    pokemon_name = pokemon_name.lower()

    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}")

    if(response.status_code == 404):
        
        error_msg = f"-{pokemon_name}- isn't a pokemon"
        error_msg = error_msg.center(CENTERING_SIZE * 3 + 6 - 2)

        print(Fore.RED + f"|{error_msg}|" + Style.RESET_ALL)

        return

    data = response.json()

    # building name message
    name_msg = data['species']['name'].capitalize()
    name_msg = name_msg.center(CENTERING_SIZE)

    if(NAME.capitalize() == data['species']['name'].capitalize()):

        # Print text in red
        print(Fore.GREEN + f"|{name_msg}|" + Style.RESET_ALL, end='')
    
    else:
        # Print text in green
        print(Fore.RED + f"|{name_msg}|" + Style.RESET_ALL, end='')
        
    new_types = [type_info['type']['name'] for type_info in data['types']]
    
    # check pokemon matching types
    matching_types = [t for t in new_types if t in TYPES]
    types_count_match = len(matching_types)

    # building types msg
    type_msg = ", ".join(new_types)
    type_msg = type_msg.center(CENTERING_SIZE)

    if(types_count_match == len(TYPES) and len(TYPES) == len(new_types)):
        print(Fore.GREEN + f"|{type_msg}|" + Style.RESET_ALL, end='')
    
    elif(types_count_match > 0):
        print(Fore.YELLOW + f"|{type_msg}|" + Style.RESET_ALL, end='')

    else:
        print(Fore.RED + f"|{type_msg}|" + Style.RESET_ALL, end='')


    # building gen msg
    up_arrow = "\u2191"
    down_arrow = "\u2193"

    new_gen_name = get_gen(data["species"]["url"])
    gen_msg = f"{new_gen_name}({GEN_DATES[new_gen_name]})"

    if(GEN_DATES[GEN_NAME] > GEN_DATES[new_gen_name]):
        gen_msg = gen_msg + up_arrow
    elif(GEN_DATES[GEN_NAME] < GEN_DATES[new_gen_name]):
        gen_msg = gen_msg + down_arrow
    
    gen_msg = gen_msg.center(CENTERING_SIZE)

    if(GEN_DATES[GEN_NAME] == GEN_DATES[new_gen_name]):
        print(Fore.GREEN + f"|{gen_msg}|" + Style.RESET_ALL, end='')
    else:
        print(Fore.RED + f"|{gen_msg}|" + Style.RESET_ALL, end='')

    # just an endline :)
    print()

    # if you get it right
    if(NAME == pokemon_name):

        congratulations_msg = f"CONGRATULATIONS!!!! YOU GOT IT RIGHT!"
        congratulations_msg = congratulations_msg.center(CENTERING_SIZE * 3 + 6 - 2)

        print(Fore.GREEN + f"|{congratulations_msg}|" + Style.RESET_ALL)

        CORRECT = True



def select_pokemon():
    global RESPONSE, DATA, NAME, TYPES, GEN_NAME

    # ids from 1 to 1010 :)
    random_id = random.randint(1, 1010)
    url = f"https://pokeapi.co/api/v2/pokemon/{random_id}"

    RESPONSE = requests.get(url)

    if RESPONSE.status_code == 200:
        DATA = RESPONSE.json()
        NAME = DATA['name']
        TYPES = [type_info['type']['name'] for type_info in DATA['types']]

        drawn_pokemon()
        
        species_url = DATA["species"]["url"]
        GEN_NAME = get_gen(species_url)

        
    else:
        print("Error fetching data.")

    print(url)

def game_loop():
    global CORRECT, NAME

    print("Quem é esse pokemon?!")
    select_pokemon()

    while(CORRECT == False):

        print_stats(input("you guess: "))



def main():
    # menu aqui
    game_loop()


main()