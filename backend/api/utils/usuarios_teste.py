from api.modelos.usuario import Usuario


def inserir_usuarios_teste(usuario_dao):
    """Cria as contas de desenvolvimento sem alterar usuários já existentes."""
    contas = (
        {"registro": 1, "nome": "Professor Teste", "email": "professor.teste@example.com", "role": "Professor"},
        {"registro": 2, "nome": "Pedagogico Teste", "email": "pedagogico.teste@example.com", "role": "Processo pedagógico"},
    )
    inseridos = 0
    for conta in contas:
        # Inclui usuários inativos: não reativa nem redefine uma conta existente.
        if usuario_dao.campo_existe("registro", conta["registro"]):
            continue
        usuario = Usuario()
        for campo, valor in conta.items():
            setattr(usuario, campo, valor)
        usuario.ativo = True
        usuario.senha = "Teste123!"
        usuario.gerar_hash_senha()
        inseridos += int(usuario_dao.criar_se_ausente(usuario))
    return inseridos
