import socket
import re
import requests
import threading
import docker

global docker_image, prefix
prefix = "koala"
docker_image = "freevm:latest"
steamninja77_at_gmail_dot_com_AUTHTOKEN = "2LPuB8ubpvx1OdIo1Rt9iqjhIUt_5gXEPS9LtmTMShYaJJYGx"
steamninja77_at_gmail_dot_com_API_KEY = "2LSV3llU08Iliz33uygx1dnFvwg_5AiT9qDcbCu2Tci5CgsBr"


def convert_str_to_snake_case_and_add_prefix(text: str) -> str:
    text = text.lower().replace(" ", "_")
    for symbol in list("!\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"):
        text = text.replace(symbol, "_symbol_")
    for number, number_string in zip(range(10), ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]):
        text = text.replace(str(number), f"_{number_string}_")
    text = "".join([char for char in text if char in "abcdefghijklmnopqrstuvwxyz_"])
    while text[-1] == "_":
        text = text[0:-1]
    while text[0] == "_":
        text = text[1:]
    while "__" in text:
        text = text.replace("__", "_")
    if not text.startswith(f"{prefix}_"):
        text = f"{prefix}_{text}"
    return text


def generate_free_port() -> int:
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def delete_container(name: str, client: docker.DockerClient) -> None:
    try:
        container = client.containers.get(name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        pass


def create_container(port: int, name: str, client: docker.DockerClient) -> None:
    delete_container(name=name, client=client)
    client.containers.run(docker_image, name=name, ports={22: port}, labels={"org.opencontainers.image.ref.name": "ubuntu"}, detach=True)


def start_ngrok_tunnel(port: int, AUTHTOKEN: str) -> threading.Thread:
    cmd = f'C:/ngrok tcp {port} --region="in" --authtoken="{AUTHTOKEN}"'
    thread = threading.Thread(target=lambda: subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess))
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

    ssh_cmd = f"ssh koala@{host} -p {port}"

    return ssh_cmd

def main(name:str,API_KEY:str,AUTHTOKEN:str) -> list[str,threading.Thread,str]:
    name = convert_str_to_snake_case_and_add_prefix(text=name)
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    container = client.containers.run(docker_image, command="sleep infinity", name=name, ports={22: 22}, detach=True)
    
    tunnel = Ngrok(authtoken=AUTHTOKEN, region='in')
    url = tunnel.tunnel(proto='tcp', port=container.attrs['HostConfig']['PortBindings']['22/tcp'][0]['HostPort'])

    ssh_cmd = f"ssh koala@{url.host} -p {url.port}"

    return ssh_cmd, container

try:
    ssh_cmd,thread,name = main(
        name="testit",
        API_KEY=steamninja77_at_gmail_dot_com_API_KEY,
        AUTHTOKEN=steamninja77_at_gmail_dot_com_AUTHTOKEN,
    )
    print(ssh_cmd)
except KeyboardInterrupt:
    # thread.join()
    delete_container(name)
