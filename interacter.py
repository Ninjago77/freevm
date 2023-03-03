import socket,subprocess,requests,re,threading,docker

global docker_image,prefix,client
prefix = "koala"
docker_image = "freevm:latest"
client = docker.from_env()


def convert_str_to_snake_case_and_add_prefix(text:str) -> str:
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
    if not text.startswith(f"{prefix}_"):
        text = f"{prefix}_{text}"
    return text
    

def delete_container(name:str) -> None:
    try:
        container = client.containers.get(name)
    except docker.errors.NotFound as e:
        return None
    else:    
        container.kill()
        container.rm()

def create_container(name:str,ssh_j_host:str) -> None:
    delete_container(name=name)
    client.containers.run(image=docker_image,name=name,detach=True,command=f"/ssh-j.com.sh {ssh_j_host}")

def get_ssh_command(name:str,ssh_j_host:str) -> str:
    ssh_cmd = f"ssh -J {ssh_j_host}@ssh-j.com koala@{client.containers.get(name).short_id}"
    return ssh_cmd

def main(name:str,ssh_j_host:str):
    name = convert_str_to_snake_case_and_add_prefix(text=name)
    create_container(name=name,ssh_j_host=ssh_j_host)
    ssh_cmd = get_ssh_command(name=name,ssh_j_host=ssh_j_host)
    return ssh_cmd,name

try:
    ssh_cmd,name = main(
        name="testit",
        ssh_j_host="bruh",
    )
    print(ssh_cmd)
except KeyboardInterrupt:
    delete_container(name)

