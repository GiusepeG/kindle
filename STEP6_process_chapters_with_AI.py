
import os
import glob
import google.generativeai as genai
import sys

def main():
    """
    Reads all .txt files from the pos_OCR directory, sends their content to the
    Gemini API for correction, and saves the output to the pos_IA directory.
    """
    try:
        # Get the API key from the environment variable
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Erro: A variável de ambiente GOOGLE_API_KEY não foi definida.")
            print("Por favor, defina a chave da API antes de executar o script.")
            sys.exit(1)

        genai.configure(api_key=api_key)

        # Define input and output directories relative to the script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        input_dir = os.path.join(script_dir, "STEP5_ocr")
        output_dir = os.path.join(script_dir, "STEP6_pos_IA")

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Find all .txt files in the input directory and its subdirectories
        file_paths = glob.glob(os.path.join(input_dir, '**', '*.txt'), recursive=True)

        if not file_paths:
            print(f"Nenhum arquivo .txt encontrado no diretório '{input_dir}'.")
            return

        print(f"Encontrados {len(file_paths)} arquivos para processar.")

        # Set up the model
        model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")

        # Process each file
        for file_path in file_paths:
            try:
                print(f"Processando arquivo: {file_path}")

                # Read the content of the input file
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                # Construct the prompt
                prompt = (
                    "Corrija a pontuação, a gramática e a ortografia deste texto extraído por OCR. "
                    "Organize-o em parágrafos coerentes e aplique formatação básica, como títulos (se houver) "
                    "e listas, para melhorar a leitura. "
                    "O output deve conter apenas o texto corrigido, sem nenhum comentário adicional. "
                    "Texto: \n\n"
                    f'"""{file_content}"""'
                )

                # Call the Gemini API
                response = model.generate_content(prompt)
                
                # Check if the response has text
                if hasattr(response, 'text'):
                    corrected_text = response.text
                else:
                    # Handle cases where the response might be blocked or empty
                    print(f"Não foi possível obter o texto corrigido para {file_path}. Resposta: {response.prompt_feedback}")
                    # Optionally, write the original content or a placeholder
                    corrected_text = f"### ERRO AO PROCESSAR O ARQUIVO ###\n\n{file_content}"


                # Construct the output file path, preserving subdirectories
                relative_path = os.path.relpath(file_path, input_dir)
                output_file_path = os.path.join(output_dir, relative_path)

                # Create subdirectory in output_dir if it doesn't exist
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                # Write the corrected text to the output file
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(corrected_text)

                print(f"Processado e salvo com sucesso em: {output_file_path}")

            except Exception as e:
                print(f"Ocorreu um erro ao processar o arquivo {file_path}: {e}")

        print("\nProcessamento concluído.")

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()
