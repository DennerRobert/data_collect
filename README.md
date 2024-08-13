# Data Collection and Analysis Project

      Este projeto visa coletar e analisar dados históricos de estações meteorológicas, utilizando Python/Django, 
      Django Rest Framework, Machine Learning, Web Scraping, API REST e Docker para orquestração de ambiente. 
      A aplicação permite o armazenamento, visualização e predição de dados temporais, como a carga da bateria
      e outros dados das estações.


Pré-requisitos

Antes de começar, você precisará ter as seguintes ferramentas instaladas em sua máquina:

    Docker e Docker Compose
    Python 3.10+


Instalação e Configuração

-> Clonar o Repositório
    
    git clone git@github.com:DennerRobert/data_collect.git
    cd data_collect


Configurar Variáveis de Ambiente

-> Crie um arquivo .env na raiz do projeto com o seguinte conteúdo:

    POSTGRES_DB=seu_banco
    POSTGRES_USER=seu_usuario
    POSTGRES_PASSWORD=sua_senha

    POSTGRES_HOST=localhost

    DEBUG=False
    DATABASE_URL=postgres://seu_usuario:sua_senha@localhost:5432/seu_banco

    Certifique-se de ajustar as configurações do banco de dados conforme necessário, substituindo usuario, senha e nome_do_banco pelas informações corretas.


Configuração do Docker

-> Construir e Executar os Containers

    docker-compose up --build

Uso da API usando Insomnia 

-> Obter o Token de Autenticação

    Endpoint: /api/token/ (ou o equivalente no seu projeto).
    Método: POST
    Corpo da Requisição:

    {
      "username": "seu_usuario",
      "password": "sua_senha"
    }

-> Configurar Autenticação no Insomnia

* Para cada requisição que requer autenticação:

  Vá para as configurações da requisição no Insomnia.

  Na seção Headers, adicione um novo cabeçalho:

      Chave: Authorization
      Valor: Bearer seu_token_de_acesso

  Isso incluirá o token em todas as suas requisições.


-> Testar os Endpoints da API

Acessando Outros Endpoints
  -> Listar Estações:

      Endpoint: /stations/
      Método: GET

  -> Adicionar Estações:
  
      Endpoint: /stations/
      Método: POST

       Corpo da Requisição:

    {
  		"external_id": "11",
  		"name": "Estação Teste 11",
  		"latitude": "-5.7945",
  		"longitude": "-35.211"
  	}

  -> Criar Dados Históricos:

      Endpoint: /stations/{id}/historical_data/
      Método: POST
      
      Corpo da Requisição:

      [
        {
            "datetime": "2024-08-01",
            "battery": 200.0,
            "station_data": "10"
        },
        {
            "datetime": "2024-08-02",
            "battery": 220.0,
            "station_data": "12"
        }
    ]

  -> Atualizar Estação:
  
      Endpoint: /stations/{id}/update/
      Método: PATCH ou PUT
      
      Corpo da Requisição: 

      {
    		"external_id": "22",
    		"name": "Estação Teste 22",
    		"latitude": "-5.7945",
    		"longitude": "-35.211"
    	}

  -> Remover Estação:

      Endpoint: /stations/{id}/
      Método: DELETE

  -> Testando o endpoint de predição temporal:

    Endpoint: /stations/analysis/
    Método: POST

    Corpo da Requisição:

    {
        "station_id": {id},
        "start_date": "2024-08-01",
        "end_date": "2024-08-05"
    }
