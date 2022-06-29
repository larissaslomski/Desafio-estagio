import logging

def transforma_numeros_para_forma_lancamento(codigo_forma_lancamento):
    switcher = {
        "01": "Crédito em Conta Corrente",
        "02": "Cheque Pagamento / Administrativo",
        "03": "DOC/TED(1)(2)",
        "04": "Cartão Salário (somente para Tipo de Serviço = '30')",
        "05": "Crédito em Conta Poupança",
        "06": "Liberação de Títulos HSBC",
        "07": "Emissão de Cheque Salário",
        "08": "Liquidação de Parcelas de Cobrança Não Registrada",
        "09": "Arrecadação de Tributos Federais",
        "10": "OP à Disposição",
        "11": "Pagamento de Contas e Tributos com Código de Barras",
        "12": "Doc Mesma Titularidade",
        "13": "Pagamento de Guias ",
        "14": "Credito em Conta Corrente Mesma Titularidade",
        "16": "Tributo - DARF Normal",
        "17": "Tributo GPS (Guia Providência Social)",
        "18": "Tributo - DARF Simples",
        "19": "Tributo - IPTU - Prefeituras",
        "20": "Pagamento com Atutenticação",
        "21": "Tributo - DARJ",
    }
    return switcher.get(codigo_forma_lancamento, "Inválido")

def formata_cnpj(cnpj_nao_formatado):
    fatia_um = cnpj_nao_formatado[:2]
    fatia_dois = cnpj_nao_formatado[2:5]
    fatia_tres = cnpj_nao_formatado[5:8]
    fatia_quatro = cnpj_nao_formatado[8:12]
    fatia_cinco = cnpj_nao_formatado[12:14]

    cnpj_formatado = "{}.{}.{}/{}-{}".format(
        fatia_um,
        fatia_dois,
        fatia_tres,
        fatia_quatro,
        fatia_cinco
    )
    return cnpj_formatado

def formata_data(data_nao_formatada):
    fatia_um = data_nao_formatada[:2]
    fatia_dois = data_nao_formatada[2:4]
    fatia_tres = data_nao_formatada[4:8]

    data_formatada = "{}/{}/{}".format(
        fatia_um,
        fatia_dois,
        fatia_tres
    )
    return data_formatada

def formata_cep(complemento_cep_nao_formatado):
    fatia_um = complemento_cep_nao_formatado[0:]
    cep_formatado = (f'-{fatia_um}')
    return cep_formatado

def remove_zero_esquerda(valor_pagamento):
    valor_sem_zero_esquerda = []
    
    while valor_pagamento[0] == "0":
        valor_pagamento = valor_pagamento[1:]
    valor_sem_zero_esquerda.append(valor_pagamento)
    
    return valor_sem_zero_esquerda[0]

def formata_valor(valor_sem_zero_esquerda):
    
    tamanho_total = len(valor_sem_zero_esquerda)
    
    tamanho_sem_centavos = tamanho_total - 2 
    
    centavos = valor_sem_zero_esquerda[tamanho_sem_centavos:tamanho_total]
    
    valor_antes_virgula = valor_sem_zero_esquerda[:tamanho_sem_centavos]
    
    if(tamanho_sem_centavos == 0):
        return "0" +  "," + centavos

    if(tamanho_sem_centavos <= 3):
        return valor_antes_virgula +  "," + centavos
        
    return "{:,}".format(int(valor_antes_virgula)).replace(',','.') + "," + centavos

def pega_info_header(linha):
    nome_empresa = linha[72:102]
    cnpj_formatado = formata_cnpj(linha[18:32])
    nome_banco = linha[102:132]
    return nome_empresa.strip() + ";" + cnpj_formatado.strip() + ";" + nome_banco.strip() + ";"

def pega_info_header_lote(linha):
    
    nome_rua_lote = linha[142:172]
    numero_local_lote = linha[172:177]
    nome_cidade_lote = linha[192:212]
    cep_lote = linha[212:217]
    final_cep_formatado = formata_cep(linha[217:220])
    sigla_estado_lote = linha[220:222]
    return nome_rua_lote.strip() + ";" + numero_local_lote.strip() + ";" + nome_cidade_lote.strip() + ";" + cep_lote.strip() + final_cep_formatado.strip() + ";" + sigla_estado_lote.strip() + "\n"

def pega_info_detalhamento(linha):
    nome_favorecido = linha[43:73]
    data_formatada = formata_data(linha[93:101])
    valor_pagamento = linha[119:134]
    valor_pagamento_sem_zero_esq = remove_zero_esquerda(valor_pagamento)
    valor_pagamento_formatado = formata_valor(valor_pagamento_sem_zero_esq)
    numero_documento_atribuido_empresa = linha[73:93]
    
    return nome_favorecido.strip() + ";" + data_formatada.strip() + ";" + "R$ " + valor_pagamento_formatado.strip() + ";" + numero_documento_atribuido_empresa.strip() + ";"

def percorre_linhas(nome_input, nome_output):
    arquivo = open(nome_input ,"r")
    output = open(nome_output , "w")

    forma_de_lancamento = ""

    for linha in arquivo:
        if linha[7] == '0':
            logging.info(" Coletando informacoes da linha de header de arquivo")
            linha_de_header_info = pega_info_header(linha)
            linha_header_saida = "Nome da Empresa;Numero de Inscricao da Empresa;Nome do Banco;Nome da Rua;Numero do Local;Nome da Cidade;CEP;Sigla do Estado \n"
            output.write(linha_header_saida)
            output.write(linha_de_header_info)

        if linha[7] == '1':
            logging.info(" Coletando informacoes da linha de header de lote")
            linha_de_lote_info = pega_info_header_lote(linha)
            linha_de_lote_saida = "\nNome do Favorecido;Data de Pagamento;Valor do Pagamento;Numero do Documento Atribuido pela Empresa;Forma de Lancamento \n"
            output.write(linha_de_lote_info)
            output.write(linha_de_lote_saida)
            forma_de_lancamento = linha[11:13]

        if linha[7] == '3':
            logging.info(" Coletando informacoes da linha de detalhe")
            linha_de_detalhamento_info = pega_info_detalhamento(linha)
            linha_de_detalhamento_info = linha_de_detalhamento_info + transforma_numeros_para_forma_lancamento(forma_de_lancamento) + "\n"
            output.write(linha_de_detalhamento_info)
            
    arquivo.close()
    output.close()