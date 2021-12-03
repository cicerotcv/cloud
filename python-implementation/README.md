# Implementação em Python

Antes de iniciar a criação da infraestrutura na AWS,
verifique se preencheu o arquivo `.env` corretamente.

Ele deve ficar mais ou menos assim:

> (os dados abaixo são apenas exemplos e não devem funcionar)

```sh
# Access Keys
AWS_ACCESS_KEY_ID=4AABFGGHHIJKLQTVWYYZ
AWS_SECRET_ACCESS_KEY=16DHIJQUYccilmoswx/2349AAAASUUYbcdglmqvy

# Mongo DB Admin Credentials
MONGO_USER=admin_username
MONGO_PWD=admin_password
MONGO_DB=admin # you should use MONGO_DB=admin

# Server
NODE_SECRET=super_secret_unique_string
```

---

## Criando a Infraestrutura

### Instale as dependências

As dependências utilizadas para a execução do projeto estão no arquivo
`requirements.txt`

    $ pip3 install -r requirements.txt

### Execute

O script `main.py` contém as instruções necessárias para executar o programa.

    $ python3 main.py

### O que esperar

Se os passos acima forem executados sem problemas, algumas mensagens deverão ser exibidas no terminal indicando que esá sendo feita uma limpeza de máquinas criadas (Instances), grupos de segurança (Security Groups), chaves de acesso SSH (KeyPairs), _load balancers_, etc.

O programa iniciará criando uma instância em **Ohio (us-east-2)** e ela será responsável pelo **Banco de Dados (MongoDB)**. Além disso, ainda em relação a Ohio, o programa deverá criar um KeyPair `key-us-east-2.key` que pode ser usado para acessar a máquina via SSH.

Em **North Virginia (us-east-1)**, o procedimento é análogo, mas possui mais passos:

1. Criação de par de chaves `key-us-east-1`;
2. Criação grupo de segurança `group-us-east-1`;
3. Crianção de instância EC2;
4. Criação de imagem a partir da instância;
5. Destruiçao da instância;
6. Criação de _launch configuration_ `lc-us-east-1`;
7. Criação de _load balancer_ `lb-us-east-1`;
8. Criação de _target group_ `tg-us-east-1`;
9. Criação de _auto scaling group_ `as-us-east-1`;

Depois disso, será exibido terminal o `DNSName` do _Load Balancer_
e com ele é possível fazer requisições ao servidor.

> **Importante**: causar uma interrupção no terminal que executou as etapas acima ocasiona na destruição da infraestrutura construída. Ou seja, o servidor só se mantém disponível enquanto o terminal estiver aberto.

### Logs

Para ter acesso aos logs do servidor, acesse via SSH e verifique o arquivo em `/home/ubuntu/server/dist/access.log` dentro da instância.

**Para acessar via SSH:**

```sh
# INSTANCE_PUBLIC_DNS pode ser encontrado no painel da AWS
ssh -i ./tmp/key-us-east-1.key ubuntu@$INSTANCE_PUBLIC_DNS
```

**Para acompanhar logs em tempo real**\
Dentro da instância, execute:

```sh
tail -f ./server/dist/access.log
```

## Interagindo com o Servidor

Para interagir com o servidor, é necessário ter acesso ao `DNSName`.

### Executando o Client

Para testar se o Servidor está acessível, execute:

```sh
python3 client.py --check
```

Para executar a aplicação `client`, certifique-se de ter instalado as dependências. Após isso, você pode executar:

```sh
python3  client.py --loadbalancer $DNSName
```

Com isso, ele irá executar cada instrução e fazer uma pausa. Pressione `enter` para continuar. Se quiser que o programa execute tudo automaticamente, acrescente a `flag` `--autorun`

```sh
python3  client.py --loadbalancer $DNSName --autorun
```
