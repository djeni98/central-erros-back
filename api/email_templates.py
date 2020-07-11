subject = 'Central de Erros - Solicitação de recuperação de senha'
message = '''Olá,

Foi feita uma solicitação de recuperação de senha para o email {email}.
Para poder trocar sua senha, acesse o link {link} e forneça as informações necessárias.

Esse link tem validade de {unit_time}.

---
Central de Erros
'''

html_message = '''<!DOCTYPE html>
<html>
<head>
</head>
<body>
<p>Olá, </br>
</br>
Foi feita uma solicitação de recuperação de senha para o email <i>{email}</i>. </br>
Para poder trocar sua senha, acesse o <a href="{link}">link</a> e forneça as informações necessárias. </br>
</br>
Esse link tem validade de {unit_time}. </br>
</br>
--- </br>
Central de Erros
</body>
</html>
'''
