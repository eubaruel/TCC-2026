from pymongo import ASCENDING, UpdateOne

from api.modelos.prova_x_aluno import Prova_x_aluno


class Prova_x_aluno_dao:
    def __init__(self, banco_de_dados_dependency):
        print("⬆️ prova_x_aluno_dao.__init__()")
        self.__banco_de_dados = banco_de_dados_dependency.get_banco_de_dados()
        self.__colecao = self.__banco_de_dados["provas_x_alunos"]

        self.__colecao.create_index(
            [
                ("id_prova", ASCENDING),
                ("matricula_aluno", ASCENDING)
            ],
            unique=True
        )

    def sincronizar(self, id_prova: str, provas_x_alunos: list[Prova_x_aluno]) -> int:
        """Substitui as versões da prova destinadas aos alunos atuais das turmas."""
        print("✅ prova_x_aluno_dao.sincronizar()")

        documentos = [self.set_doc(objeto) for objeto in provas_x_alunos]
        matriculas = [documento["matricula_aluno"] for documento in documentos]

        if documentos:
            operacoes = [
                UpdateOne(
                    {
                        "id_prova": documento["id_prova"],
                        "matricula_aluno": documento["matricula_aluno"]
                    },
                    {"$set": documento},
                    upsert=True
                )
                for documento in documentos
            ]
            self.__colecao.bulk_write(operacoes, ordered=False)

        filtro_obsoletos = {"id_prova": id_prova}
        if matriculas:
            filtro_obsoletos["matricula_aluno"] = {"$nin": matriculas}
        self.__colecao.delete_many(filtro_obsoletos)

        return len(documentos)

    def buscar_por_id_prova(self, id_prova: str) -> list[dict]:
        print("✅ prova_x_aluno_dao.buscar_por_id_prova()")

        return list(
            self.__colecao.find(
                {"id_prova": id_prova},
                {"_id": 0}
            ).sort("matricula_aluno", ASCENDING)
        )

    @staticmethod
    def set_doc(obj_prova_x_aluno: Prova_x_aluno) -> dict:
        return {
            "matricula_aluno": obj_prova_x_aluno.matricula_aluno,
            "id_prova": obj_prova_x_aluno.id_prova,
            "questoes": [questao.copy() for questao in obj_prova_x_aluno.questoes]
        }
