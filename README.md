> Aceleração Dev de Python da CodeNation

# Central de Erros - Back-end

Desenvolvimento de um sistema para centralizar registros de erros.

## Implementação

Para seguir a especificação do [desafio](desafio.md), foram escolhidas algumas tecnologias e ferramentas, como:

* [Django](https://www.djangoproject.com/) ```3.0.7```
* [Django Rest Framework](https://www.django-rest-framework.org/) ```3.11.0```
* [Swagger](https://swagger.io/) ```2.0```

## Instalação

### Clone do Repositório
```bash
$ git clone https://github.com/djeni98/central-erros-back.git
```

### Configurando Ambiente
```bash
$ cd central-erros-back
$ pip3 install virtualenv
$ virtualenv venv -p python3
$ source venv/bin/activate 
(venv) $ pip install -r requirements.txt
```

### Configurando o sistema
```bash
(venv) $ python manage.py migrate
(venv) $ python manage.py createsuperuser
```

### Executando o sistema
```bash
(venv) $ python manage.py runserver
```

Pela configuração padrão, os endpoints são renderizados com [BrowsableAPIRenderer](https://www.django-rest-framework.org/api-guide/renderers/#browsableapirenderer) do rest\_framework.
Para poder usar visualizar o funcionamento de produção é preciso exportar duas variáveis de ambiente e copiar arquivos estáticos para somente um lugar.

```bash
(venv) $ export DJANGO_SETTINGS_MODULE='centralErros.settings_prod'
(venv) $ export DATABASE_URL='sqlite:///db.sqlite3'
(venv) $ python manage.py collectstatic
(venv) $ python manage.py runserver
```

## Endpoints

Os endpoints estão especificados no arquivo [swagger.yaml](api/static/swagger.yaml). Para visualizar a página da especificação, execute a aplicação e acesse o endereço `http://127.0.0.1:8000/api/docs/`.

## Deploy

[![Build Status](https://travis-ci.com/djeni98/central-erros-back.svg?branch=master)](https://travis-ci.com/djeni98/central-erros-back)

Para fazer o deploy da [aplicação](https://djeni98-central-de-erros.herokuapp.com/api/), foi utizado as seguintes plataformas:

* [Travis CI](https://travis-ci.com/)
* [Heroku](https://www.heroku.com/)
