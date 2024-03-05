class MissAuthorization(Exception):  # Sem a autorização no cabeçalho.
    pass

class InvalidToken(Exception):  # Token invalido.
    pass

class InvaliUser(Exception):  # Usuário inválido.
    pass

