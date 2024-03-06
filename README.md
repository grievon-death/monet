## Monitoring Network [MonNet]

### Dependências.

- python3.10 ou compatível.
- python3-pip
- MongoDB

---

### Como usar.

Primeiramente, será necessário realizar alterações, de acordo com o seu ambiente, no arquivo `conf.json` que fica na raiz do projeto. Os valores padrão são:

```json
{
    "refreshTime": 1,  // Tempo em que os daemons capturam as informações da rede.
    "logLevel": "error",  // Nível de log do programa.
    "mongoHost": "mongodb://monet.mongo",  // Hostname do banco de dados. Apontando para o container do docker-compose.yml
    "mongoPort": 27017,  // Porta do banco de dados.
    "mongoName": "monet",  // Nome do banco de dados.
    "mongoExpireDataSeconds": 3600,  // Tempo de expiração dos dados no banco.
    "mongoResponseLimit": 100,  // A aplicação usa motor, então é necessário limitar o tamanho da resposta.
    "debug": false,  //  API REST em modo de debug?
    "appSecretKey": "serw#%@rqdÀWRPA`SDosd123@!13qweqsd-as=-%¨&ÏYJ"  // Senha para os cookies da API REST, recomento trocar por uma senha forte.
}
```

#### Local.

Instale os pacotes necessários.

```bash
$ pip install -r requirements.txt
```

Rode localmente o comando que realiza as migrações necessárias no banco de dados. Ele é importante para criar os indíces da aplicação.

```bash
$ python3 monet.py migrate
```

Rode localmente o comando que inicia os daemons de processamento.

```bash
$ python3 monet.py daemons
```

> **OBS:** Se estiver usando linux e possuir o programa make instalado, os dois comandos a cima podem ser substituídos por "make daemons" que migra e inicia os daemons


Finalmente rode localmente o comando que inicia a API REST que mostra os dados.

```bash
$ python3 monet.py rest
```

> **OBS:** Se estiver usando linux e possuir o programa make instalado, o comando pode ser substituído por "make rest"


#### Docker & Docker compose

Para erguer as imagens no container Docker basta usar o comando a seguir, o comando irá montar a imagem e executar os daemons e API, já com um banco de dados:

```bash
$ docker compose up
```

Ou no modo daemon:

```bash
$ docker compose up -d
```

---

### API REST

A API REST estará disponível na porta 5005 da sua máquina.

#### Rotas

| Rota | Conteúdo | Permitido |
| ---- | -------- | --------- |
| /api/login/ | Realiza o login e retorna um token de acesso. Usuário e senha padrão é `admin` | POST |
| /api/interfaces/ | Interfaces de rede disponível e dados de conexão em bytes | GET |
| /api/connections/ | Conexões que estão em uso na máquina e seu PID | GET |
| /api/packages/ | Pacotes trafegados pela máquina | GET |


Coloque o token gerado no login no cabeçalho `Authorization` das requisições das demais rotas!
