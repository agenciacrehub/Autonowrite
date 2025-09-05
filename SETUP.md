# Guia de Setup - AutonoWrite

## 1. Preparação do Ambiente

### 1.1 Criar e ativar ambiente virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Linux/Mac:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate
```

### 1.2 Instalar dependências

```bash
pip install -r requirements.txt
```

## 2. Configuração

### 2.1 Configurar chave da API Groq

1. Crie uma conta em [Groq Console](https://console.groq.com/)
2. Vá em "API Keys" e crie uma nova chave
3. Crie ou edite o arquivo `.env`:

```bash
echo "GROQ_API_KEY=sua_chave_aqui" > .env
```

### 2.2 Estrutura de diretórios

O script criará automaticamente os diretórios necessários:
- `results/` - Resultados das execuções
- `experiments/` - Dados de experimentos
- `reports/` - Relatórios gerados

## 3. Validação

Execute o script de validação para verificar se tudo está configurado corretamente:

```bash
python validate.py
```

## 4. Uso

Execute o sistema principal:

```bash
python main.py
```

## 5. Opções de Execução

### 5.1 Usando Ollama (opcional)

1. Instale o Ollama:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. Baixe um modelo (ex: llama3):
   ```bash
   ollama pull llama3
   ```

3. Execute com o provider Ollama:
   ```bash
   python main.py --provider ollama
   ```

### 5.2 Modo de Simulação

Para testes sem conexão com APIs:

```bash
python main.py --provider simulation
```

## Solução de Problemas

### Erro: "GROQ_API_KEY não encontrada"
- Verifique se o arquivo `.env` existe e contém a chave correta
- Certifique-se de que o arquivo está no diretório raiz do projeto

### Erro: Módulos não encontrados
- Ative o ambiente virtual
- Execute `pip install -r requirements.txt`

### Performance lenta
- Reduza o número de iterações
- Use um modelo menor (ex: `--model llama3-8b-8192`)

## Licença

MIT License
