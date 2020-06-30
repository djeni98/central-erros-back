> Aceleração Dev de Python da CodeNation

# Central de Erros - Back-end

Desenvolvimento de um sistema para centralizar registros de erros.

## Implementação

Para seguir a especificação do [desafio](desafio.md), foram escolhidas algumas tecnologias e ferramentas, como:

* [Django](https://www.djangoproject.com/) ```3.0.7```
* [Django Rest Framework](https://www.django-rest-framework.org/) ```3.11.0```

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
(venv) $ python manage.py makemigrations 
(venv) $ python manage.py migrate
(venv) $ python manage.py createsuperuser
```

### Executando o sistema
```bash
(venv) $ python manage.py runserver
```
