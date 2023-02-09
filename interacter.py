import socket,subprocess,requests,re,threading

global docker_image
docker_image = "freevm:latest"
steamninja77_at_gmail_dot_com_AUTHTOKEN = "2LPuB8ubpvx1OdIo1Rt9iqjhIUt_5gXEPS9LtmTMShYaJJYGx"
steamninja77_at_gmail_dot_com_API_KEY = "2LSV3llU08Iliz33uygx1dnFvwg_5AiT9qDcbCu2Tci5CgsBr"

def convert_str_to_snake_case(text:str) -> str:
    text = text.lower().replace(" ","_")
    for symbol in list("!\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"):
        text = text.replace(symbol,"_symbol_")
    for number,number_string in zip(range(10),["zero","one","two","three","four","five","six","seven","eight","nine"]):
        text = text.replace(str(number),f"_{number_string}_")
    text = "".join([char for char in text if char in "abcdefghijklmnopqrstuvwxyz_"])
    while text[-1] == "_":
        text = text[0:-1]
    while text[0] == "_":
        text = text[1:]
    while "__" in text:
        text = text.replace("__","_")
    return text
    

def generate_free_port() -> int:
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    del sock
    return port

def delete_container(name:str) -> None:
    [
        subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for cmd in [
            f"\"C:\Program Files\Docker\Docker\\resources\\bin\docker.exe\" kill {name}",
            f"\"C:\Program Files\Docker\Docker\\resources\\bin\docker.exe\" rm {name}",
        ]
    ]

def create_container(port:int,name:str) -> None:
    delete_container(name=name)
    cmd = f"\"C:\Program Files\Docker\Docker\\resources\\bin\docker.exe\" run --env=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin -p {port}:22 --label='org.opencontainers.image.ref.name=ubuntu' --label='org.opencontainers.image.version=22.04' --runtime=runc --name={name} -d {docker_image}"
    subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def start_ngrok_tunnel(port:int,AUTHTOKEN:str) -> threading.Thread:
    cmd = f'C:/ngrok tcp {port} --region="in" --authtoken="{AUTHTOKEN}"'
    thread = threading.Thread(target=lambda:subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),args=())
    thread.start()
    return thread

def get_ssh_command(API_KEY:str) -> str:
    url = "https://api.ngrok.com/tunnels"
    headers = {
        "Authorization":f"Bearer {API_KEY}",
        "Ngrok-Version":"2",
    }
    response = requests.get(url=url,headers=headers).json()

    tunnels = response["tunnels"]
    tunnel = tunnels[0]
    public_url = tunnel["public_url"]

    match = re.match(r"^tcp://(?P<host>\d+\.tcp\.\w+\.ngrok\.io):(?P<port>\d+)$",public_url)
    host,port = match.group("host"),match.group("port")

    ssh_cmd = f"ssh theuser@{host} -p {port}"

    return ssh_cmd

def main(name:str,API_KEY:str,AUTHTOKEN:str) -> list[str,threading.Thread,str]:
    name = convert_str_to_snake_case(text=name)
    port = generate_free_port()
    thread = start_ngrok_tunnel(port=port,AUTHTOKEN=AUTHTOKEN)
    create_container(port=port,name=name)
    ssh_cmd = get_ssh_command(API_KEY=API_KEY)
    return ssh_cmd,thread,name

try:
    ssh_cmd,thread,name = main(
        name="slash_test",
        API_KEY=steamninja77_at_gmail_dot_com_API_KEY,
        AUTHTOKEN=steamninja77_at_gmail_dot_com_AUTHTOKEN,
    )
    print(ssh_cmd)
except KeyboardInterrupt:
    thread.join()
    delete_container(name)

