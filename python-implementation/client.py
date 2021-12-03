import requests
from time import sleep
from controller.utils import random_str, print_json
from controller.logger import logger
import argparse


BASE_URL = None
AUTO_RUN = None
AUTH_HEADER = 'x-authorization'

# authentication routes
CHECK_AUTHORIZATION = '/auth'  # GET
CREATE_ACCOUNT = '/auth/create-account'  # POST
DELETE_ACCOUNT = '/auth/delete'  # POST
LOGIN = '/auth/login'  # POST

# tasks routes
LIST_TASKS = "/tasks"  # GET
GET_TASK = "/task/"  # GET + task_id
DELETE_TASK = "/task/"  # DELETE + task_id
CREATE_TASK = "/task"  # POST
UPDATE_TASK = "/task/"  # PATCH + task_id


def parse_args():
    parser = argparse.ArgumentParser(
        description='Interact with AWS LoadBalancer+AutoScaling instances')
    parser.add_argument("-l", "--loadbalancer",
                        help="Load Balancer DNSName",
                        default='localhost:8080')
    parser.add_argument("-a", "--autorun",
                        action='store_true',
                        help="Defines if wether the program should run automatically or waits for user input",
                        default=False)
    parser.add_argument("-t", "--test",
                        action='store_true',
                        help="Defines if wether the program should execute or just test connectivity",
                        default=False)

    return parser.parse_args()


class Waiter():
    def __init__(self, auto: bool = False, time=2):
        if auto:
            self.wait = lambda: sleep(time)
        else:
            self.wait = input


class Requests():
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.auth_header = None

    def update_header(self, res):
        custom_header = res.headers.get(AUTH_HEADER, None)
        if custom_header:
            self.auth_header = custom_header

    def get_headers(self):
        return {AUTH_HEADER: self.auth_header}

    def test_connection(self):
        url = self.base_url
        response = requests.get(url)
        logger.log(f"Status Code: {response.status_code}")
        return response.status_code == 200

    def check_authorization(self):
        url = self.base_url + CHECK_AUTHORIZATION
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        self.update_header(response)
        return response

    def create_account(self, body):
        url = self.base_url + CREATE_ACCOUNT
        response = requests.post(url, json=body)
        self.update_header(response)
        return response

    def login(self, body):
        url = self.base_url + LOGIN
        response = requests.post(url, json=body)
        self.update_header(response)
        return response

    def delete_account(self, body):
        url = self.base_url+DELETE_ACCOUNT
        response = requests.post(url, json=body)
        return response

    def list_tasks(self):
        url = self.base_url + LIST_TASKS
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        self.update_header(response)
        return response

    def create_task(self, body):
        url = self.base_url + CREATE_TASK
        headers = self.get_headers()
        response = requests.post(url, json=body, headers=headers)
        self.update_header(response)
        return response

    def get_task(self, task_id):
        url = self.base_url + GET_TASK + task_id
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        self.update_header(response)
        return response

    def delete_task(self, task_id):
        url = self.base_url + DELETE_TASK + task_id
        headers = self.get_headers()
        response = requests.delete(url, headers=headers)
        self.update_header(response)
        return response

    def update_task(self, task_id, body):
        url = self.base_url + UPDATE_TASK + task_id
        headers = self.get_headers()
        response = requests.patch(url, json=body, headers=headers)
        self.update_header(response)
        return response


class User():
    def __init__(self):
        self.username = 'user_' + random_str(3)
        self.password = random_str(10)
        self._id: str = None
        self.tasks = []
        self.requests = Requests(BASE_URL)

    @property
    def email(self):
        return f"{self.username}@cloudclient.com"

    def describe(self):
        print(f"Username: '{self.username}'")
        print(f"Email: '{self.email}'")
        print(f"Password: '{self.password}'")

    def create_account(self):
        body = {"email": self.email,
                "password": self.password,
                "username": self.username}
        res = self.requests.create_account(body)
        data = res.json()
        if res.ok:
            self._id = data['_id']
        print_json(data)

    def login(self):
        body = {"email": self.email, "password": self.password}
        res = self.requests.login(body)
        data = res.json()
        print_json(data)
        print(res.headers[AUTH_HEADER])

    def check_authorization(self):
        res = self.requests.check_authorization()
        data = res.json()
        print_json(data)

    def delete_account(self):
        body = {"email": self.email, "password": self.password}
        res = self.requests.delete_account(body)
        data = res.json()
        print_json(data)

    def list_tasks(self):
        res = self.requests.list_tasks()
        data = res.json()
        print_json(data)

    def create_task(self, content: str):
        body = {"content": content}
        res = self.requests.create_task(body)
        data = res.json()
        print_json(data)
        task_id = data['_id']
        self.tasks.append(task_id)
        return task_id

    def get_task(self, task_id: str):
        res = self.requests.get_task(task_id)
        data = res.json()
        print_json(data)

    def delete_task(self, task_id: str):
        res = self.requests.delete_task(task_id)
        data = res.json()
        print_json(data)

    def update_task(self, task_id: str, content: str):
        body = {"content": content}
        res = self.requests.update_task(task_id, body)
        data = res.json()
        print_json(data)


def test():
    req = Requests(base_url=BASE_URL)
    try:
        if req.test_connection():
            logger.log(f"Connection available")
    except:
        logger.error(f"Couldn't connect to the server at '{BASE_URL}'.")


def main():
    waiter = Waiter(auto=AUTO_RUN)
    user = User()

    logger.warn(f"# Criando usuário {user.username}")
    user.create_account()

    waiter.wait()

    logger.warn(f"# Verificando se token é válido")
    logger.warn(f"# Token: '{user.requests.auth_header}'")
    waiter.wait()
    user.check_authorization()

    logger.warn(f"# Destruindo o token localmente")
    user.requests.auth_header = None
    logger.warn(f"# Token: '{user.requests.auth_header}'")
    waiter.wait()

    logger.warn(f"# Testando autenticação sem token")
    user.check_authorization()
    waiter.wait()

    logger.warn(f"# Fazendo login com o usuário {user.username}")
    user.login()
    waiter.wait()

    logger.warn(f"# Testando autenticação")
    user.check_authorization()
    waiter.wait()

    print()

    logger.warn(f"# Listando tasks do user '{user._id}'")
    user.list_tasks()
    waiter.wait()

    logger.warn(f"# Criando 'Task 1'")
    task_id1 = user.create_task("Task 1: Terminar H0")
    waiter.wait()

    logger.warn(f"# Criando 'Task 2'")
    task_id2 = user.create_task("Task 2: Enviar email pedindo adiamento")
    waiter.wait()

    logger.warn(f"# Criando 'Task 3'")
    task_id3 = user.create_task("Task 3: Fazer 'git push' antes das 23:59")
    waiter.wait()

    logger.warn(f"# Baixando informações da task '{task_id1}'")
    user.get_task(task_id1)
    waiter.wait()

    logger.warn(f"# Alterando informações da task 'Task 1'")
    user.update_task(task_id1, "Task 1: Enviar o H0")
    waiter.wait()

    logger.warn(f"# Baixando informações da task '{task_id2}'")
    user.get_task(task_id2)
    waiter.wait()

    logger.warn(f"# Baixando informações da task '{task_id3}'")
    user.get_task(task_id3)
    waiter.wait()

    logger.warn(f"# Listando tasks do user '{user._id}'")
    user.list_tasks()
    waiter.wait()

    for task_id in user.tasks:
        logger.warn(f"# Deletando task '{task_id}'")
        user.delete_task(task_id)
        waiter.wait()

    logger.warn(f"# Deletando user '{user._id}'")
    user.delete_account()


if __name__ == "__main__":
    args = parse_args()

    BASE_URL = "http://" + args.loadbalancer
    AUTO_RUN = args.autorun
    is_testing = args.test

    if is_testing:
        test()
    else:
        main()
