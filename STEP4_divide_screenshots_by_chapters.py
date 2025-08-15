import os
import shutil

def organizar_screenshots_por_capitulos():
    """
    Lê arquivos de uma pasta de origem, identifica os pontos de divisão de capítulos
    a partir de uma outra pasta, e copia os arquivos sequencialmente para
    subpastas de capítulos numeradas em um diretório de destino.
    """
    # --- CONFIGURAÇÃO DOS DIRETÓRIOS ---
    # Altere os nomes abaixo conforme a sua estrutura de pastas.
    # OBS: O '@' nos nomes dos diretórios pode causar problemas em alguns sistemas.
    # Se encontrar erros, remova o '@' dos nomes das pastas e do código.
    
    # Pasta contendo TODOS os arquivos de screenshot em ordem.
    pasta_screenshots = "STEP2_get_screenshots"
    
    # Pasta contendo apenas os arquivos que marcam o INÍCIO de cada capítulo.
    pasta_marcadores_capitulos = "STEP3_new_chapters_screenshots"
    
    # Pasta de destino onde as subpastas (01, 02, 03...) serão criadas.
    pasta_destino = "STEP4_screenshots_divided_by_chapters"

    # --- VERIFICAÇÃO DOS DIRETÓRIOS DE ORIGEM ---
    if not os.path.isdir(pasta_screenshots):
        print(f"Erro: O diretório de screenshots '{pasta_screenshots}' não foi encontrado.")
        return
    if not os.path.isdir(pasta_marcadores_capitulos):
        print(f"Erro: O diretório de marcadores '{pasta_marcadores_capitulos}' não foi encontrado.")
        return

    # --- CRIAÇÃO DO DIRETÓRIO DE DESTINO ---
    if not os.path.exists(pasta_destino):
        print(f"Criando diretório de destino: '{pasta_destino}'")
        os.makedirs(pasta_destino)

    # --- LEITURA E ORDENAÇÃO DOS ARQUIVOS ---
    try:
        # Lista todos os arquivos na pasta de screenshots e os ordena
        todos_os_arquivos = sorted([f for f in os.listdir(pasta_screenshots) if os.path.isfile(os.path.join(pasta_screenshots, f))])
        
        # Lista os arquivos que marcam o início dos capítulos e os ordena
        marcadores = sorted([f for f in os.listdir(pasta_marcadores_capitulos) if os.path.isfile(os.path.join(pasta_marcadores_capitulos, f))])

        if not todos_os_arquivos:
            print(f"Aviso: Não há arquivos na pasta de screenshots '{pasta_screenshots}'.")
            return
        if not marcadores:
            print(f"Aviso: Não há arquivos marcadores em '{pasta_marcadores_capitulos}'.")
            return

    except OSError as e:
        print(f"Erro ao ler os arquivos: {e}")
        return

    # --- PROCESSAMENTO E CÓPIA DOS CAPÍTULOS ---
    for i, marcador_inicio in enumerate(marcadores):
        numero_capitulo = i + 1
        nome_pasta_capitulo = f"{numero_capitulo:02d}" # Formata como '01', '02', etc.
        caminho_pasta_capitulo = os.path.join(pasta_destino, nome_pasta_capitulo)

        # Cria a subpasta para o capítulo atual
        if not os.path.exists(caminho_pasta_capitulo):
            os.makedirs(caminho_pasta_capitulo)
            
        print(f"\n--- Processando Capítulo {nome_pasta_capitulo} ---")

        try:
            # Encontra o índice do arquivo que inicia o capítulo
            idx_inicio = todos_os_arquivos.index(marcador_inicio)
        except ValueError:
            print(f"Aviso: O arquivo marcador '{marcador_inicio}' não foi encontrado em '{pasta_screenshots}'. Pulando para o próximo.")
            continue

        # Determina o final do intervalo do capítulo
        idx_fim = len(todos_os_arquivos) # Por padrão, vai até o final
        
        # Se não for o último marcador, o fim é o início do próximo capítulo
        if i + 1 < len(marcadores):
            proximo_marcador = marcadores[i+1]
            try:
                # O índice final é o do próximo marcador (não inclusivo)
                idx_fim = todos_os_arquivos.index(proximo_marcador)
            except ValueError:
                print(f"Aviso: O próximo marcador '{proximo_marcador}' não foi encontrado em '{pasta_screenshots}'. O capítulo {nome_pasta_capitulo} irá até o final.")
        
        # Seleciona os arquivos que pertencem a este capítulo
        arquivos_do_capitulo = todos_os_arquivos[idx_inicio:idx_fim]
        
        if not arquivos_do_capitulo:
            print(f"Nenhum arquivo encontrado para o Capítulo {nome_pasta_capitulo}.")
            continue

        print(f"Copiando {len(arquivos_do_capitulo)} arquivos para a pasta '{nome_pasta_capitulo}'...")
        
        # Copia cada arquivo para a pasta de destino do capítulo
        for nome_arquivo in arquivos_do_capitulo:
            caminho_origem = os.path.join(pasta_screenshots, nome_arquivo)
            caminho_destino_arquivo = os.path.join(caminho_pasta_capitulo, nome_arquivo)
            # print(f"Copiando: {nome_arquivo}") # Descomente para ver cada arquivo sendo copiado
            shutil.copy2(caminho_origem, caminho_destino_arquivo)

    print("\nProcesso de organização concluído com sucesso!")

# --- EXECUÇÃO DO SCRIPT ---
if __name__ == "__main__":
    organizar_screenshots_por_capitulos()