#  Bot de Lista de Compras Discord
 
Um bot do Discord simples para gerenciar listas de compras de forma organizada e eficiente.

##  Funcionalidades

- 📝 Adicionar itens com quantidade, preço e descrição
- 📋 Visualizar listas paginadas
- ✏️ Editar itens existentes
- 🗑️ Remover itens específicos
- 🧹 Limpar listas inteiras
- 💾 Backup automático dos dados
- 🎨 Interface bonita com embeds coloridos

##  Instalação

1. Clone o repositório:
```bash
git clone  https://github.com/danilo-araujo0000/-lista-de-compras-
cd [NOME_DA_PASTA]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env`:
```env
DISCORD_TOKEN=token
```

4. Execute o bot:
```bash
python main.py
```

##  Comandos

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `!add` | Adiciona um item à lista | `!add compras janeiro 2 pães $5.50 == integral` |
| `!compras` | Mostra a lista de compras | `!compras janeiro 1` |
| `!editar` | Edita um item da lista | `!editar compras janeiro 1 3 pães $6.00` |
| `!remove` | Remove um item da lista | `!remove compras janeiro "2 pães"` |
| `!limpar` | Limpa uma lista inteira | `!limpar compras janeiro` |
| `!ajuda` | Mostra todos os comandos | `!ajuda` |

##  Formato dos Itens

O bot suporta um formato flexível para os itens:
- **Quantidade**: Número no início (opcional)
- **Preço**: Usando `$` (opcional)
- **Descrição**: Usando `==` (opcional)

Exemplo completo:
```
!add compras janeiro 2 pães $5.50 == integral
```

##  Segurança

- Token do bot armazenado em arquivo `.env`
- Backup automático dos dados
- Confirmação para ações destrutivas

##  Estrutura de Arquivos

```
├── main.py           # Código principal do bot
├── config.py         # Configurações e constantes
├── .env             # Variáveis de ambiente
├── requirements.txt  # Dependências
├── compras.json     # Dados das listas
└── backups/         # Backups automáticos
```

##  Tecnologias Utilizadas

- Python 3.8+
- discord.py 2.3.2
- python-dotenv 1.0.0

##  Requisitos do Sistema

- Python 3.8 ou superior
- Conexão com internet
- Token de bot do Discord

##  Contribuindo

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request


##  Próximas Atualizações

- [ ] Suporte a múltiplos servidores
- [ ] Estatísticas de compras
- [ ] Categorias customizáveis
- [ ] Exportação de listas
- [ ] Lembretes de compras
