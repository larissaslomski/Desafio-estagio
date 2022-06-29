
import sys
from gera_relatorio import percorre_linhas

import logging


logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    logging.info(" Gerando relatório")

    nome_classe, nome_input, nome_output = sys.argv

    percorre_linhas(nome_input, nome_output)

    logging.info(" Relatório gerado")
