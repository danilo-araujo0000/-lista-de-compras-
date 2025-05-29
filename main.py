import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
from datetime import datetime
import shutil
from config import *

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True  
bot = commands.Bot(command_prefix=PREFIX, intents=intents, enable_debug_events=True)

bot._connection._voice_clients = {}

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        listas = json.load(f)
else:
    listas = {}

def fazer_backup():
    """Cria um backup do arquivo de dados"""
    if os.path.exists(DATA_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{BACKUP_DIR}/compras_backup_{timestamp}.json"
        shutil.copy2(DATA_FILE, backup_file)

def salvar():
    """Salva os dados e cria um backup"""
    with open(DATA_FILE, 'w') as f:
        json.dump(listas, f, indent=2)
    fazer_backup()

@bot.event
async def on_ready():
    print(f'{bot.user} está online e pronto!')
    await bot.change_presence(activity=discord.Game(name=f"Use {PREFIX}ajuda"))

@bot.command(name='add')
async def adicionar(ctx, categoria: str, mes: str, *, item: str):
    """Adiciona um item à lista com suporte a preços"""
    await ctx.message.delete()

    chave = f"{categoria.lower()}_{mes.lower()}"
    if chave not in listas:
        listas[chave] = []

    linhas_filtradas = [linha for linha in item.splitlines() if not linha.strip().startswith('!')]
    item_limpo = ' '.join(linhas_filtradas).strip()

    preco = None
    if '$' in item_limpo:
        item_parte, preco_str = item_limpo.split('$', 1)
        try:
            preco = float(preco_str.split()[0].replace(',', '.'))
            item_limpo = item_parte.strip()
        except ValueError:
            pass

    if '==' in item_limpo:
        item_parte, descricao = item_limpo.split('==', 1)
        descricao = descricao.strip()
    else:
        item_parte = item_limpo
        descricao = ""

    partes = item_parte.strip().split(" ", 1)
    if len(partes) == 2 and partes[0].isdigit():
        quantidade = int(partes[0])
        nome_item = partes[1].strip()
        
        item_formatado = f"{quantidade} {nome_item}"
        if preco:
            item_formatado += f" (R$ {preco:.2f})"
        if descricao:
            item_formatado += f" --> {descricao}"
        
        encontrado = False
        for i, existente in enumerate(listas[chave]):
            if nome_item in existente:
                partes_existente = existente.split(" ", 1)
                if len(partes_existente) >= 2 and partes_existente[0].isdigit():
                    quantidade_total = int(partes_existente[0]) + quantidade
                    listas[chave][i] = f"{quantidade_total} {nome_item}"
                    if preco:
                        listas[chave][i] += f" (R$ {preco:.2f})"
                    if descricao:
                        listas[chave][i] += f" --> {descricao}"
                    encontrado = True
                    break
        
        if not encontrado:
            listas[chave].append(item_formatado)
    else:
        listas[chave].append(item_parte.strip())

    listas[f"{chave}_modificado"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    salvar()

    embed = discord.Embed(
        title=MESSAGES['item_added'],
        description=(
            f"📋 **Lista:** {categoria.capitalize()} - {mes.capitalize()}\n"
            f"➕ **Novo item:** `{item_formatado if 'item_formatado' in locals() else item_parte.strip()}`\n"
            f"🕒 **Atualizado em:** {listas[f'{chave}_modificado']}"
        ),
        color=COLORS['success']
    )
    await ctx.send(embed=embed)

class NavegacaoView(View):
    def __init__(self, mes: str, pagina: int, total_pages: int):
        super().__init__(timeout=60)
        self.mes = mes
        self.pagina = pagina
        self.total_pages = total_pages
        
        primeira_pagina = Button(label="⏮️ Primeira", style=discord.ButtonStyle.gray, disabled=(pagina == 1))
        primeira_pagina.callback = self.primeira_pagina_callback
        self.add_item(primeira_pagina)
        
        anterior = Button(label="◀️ Anterior", style=discord.ButtonStyle.blurple, disabled=(pagina == 1))
        anterior.callback = self.anterior_callback
        self.add_item(anterior)
        
        atual = Button(label=f"📄 {pagina}/{total_pages}", style=discord.ButtonStyle.gray, disabled=True)
        self.add_item(atual)
        
        proximo = Button(label="▶️ Próximo", style=discord.ButtonStyle.blurple, disabled=(pagina == total_pages))
        proximo.callback = self.proximo_callback
        self.add_item(proximo)
        
        ultima_pagina = Button(label="⏭️ Última", style=discord.ButtonStyle.gray, disabled=(pagina == total_pages))
        ultima_pagina.callback = self.ultima_pagina_callback
        self.add_item(ultima_pagina)
        
        atualizar = Button(label="🔄 Atualizar", style=discord.ButtonStyle.green)
        atualizar.callback = self.atualizar_callback
        self.add_item(atualizar)

    async def primeira_pagina_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await mostrar_lista_pagina(interaction, self.mes, 1)

    async def anterior_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await mostrar_lista_pagina(interaction, self.mes, self.pagina - 1)

    async def proximo_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await mostrar_lista_pagina(interaction, self.mes, self.pagina + 1)

    async def ultima_pagina_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await mostrar_lista_pagina(interaction, self.mes, self.total_pages)

    async def atualizar_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await mostrar_lista_pagina(interaction, self.mes, self.pagina)

async def mostrar_lista_pagina(interaction_or_ctx, mes: str, pagina: int = 1):
    """Função auxiliar para mostrar uma página específica da lista"""
    chave = f"compras_{mes.lower()}"
    
    if chave not in listas or not listas[chave]:
        embed = discord.Embed(
            title="Lista Vazia",
            description="Nenhum item encontrado nesta lista.\nUse `!add compras {mes} item` para adicionar itens.",
            color=COLORS['error']
        )
        if isinstance(interaction_or_ctx, discord.Interaction):
            if interaction_or_ctx.message:
                await interaction_or_ctx.message.edit(embed=embed, view=None)
        else:
            await interaction_or_ctx.send(embed=embed)
        return

    total_items = len(listas[chave])
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    pagina = max(1, min(pagina, total_pages))
    
    start_idx = (pagina - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    items_pagina = listas[chave][start_idx:end_idx]
    
    lista_formatada = []
    total_valor = 0.0
    
    for i, item in enumerate(items_pagina, start=start_idx + 1):
        if i > start_idx + 1:
            lista_formatada.append("")
            
        if "R$" in item:
            try:
                nome, preco_part = item.split("(R$")
                preco_str = preco_part.split(")")[0].strip()
                preco = float(preco_str.replace(",", "."))
                total_valor += preco
                
                item_formatado = f"**{i}.** {nome.strip()} • R$ {preco:.2f}"
                
                if "-->" in item:
                    desc = item.split("-->")[1].strip()
                    item_formatado += f"\n*{desc}*"
                
                lista_formatada.append(item_formatado)
            except:
                lista_formatada.append(f"**{i}.** {item}")
        else:
            if "-->" in item:
                nome, desc = item.split("-->")
                lista_formatada.append(f"**{i}.** {nome.strip()}\n*{desc.strip()}*")
            else:
                lista_formatada.append(f"**{i}.** {item}")
    
    lista_texto = "\n\n".join(lista_formatada)
    ultima_mod = listas.get(f"{chave}_modificado", "Não registrado")

    embed = discord.Embed(
        title=f"Lista de Compras - {mes.capitalize()}",
        description=lista_texto,
        color=COLORS['info']
    )
    
    info_texto = []
    if total_valor > 0:
        info_texto.append(f"Total: R$ {total_valor:.2f}")
    info_texto.append(f"Itens: {total_items}")
    info_texto.append(f"Página {pagina}/{total_pages}")
    
    embed.set_footer(text=" • ".join(info_texto))
    
    view = NavegacaoView(mes, pagina, total_pages)
    
    if isinstance(interaction_or_ctx, discord.Interaction):
        if interaction_or_ctx.message:
            await interaction_or_ctx.message.edit(embed=embed, view=view)
    else:
        await interaction_or_ctx.send(embed=embed, view=view)

@bot.command(name='compras')
async def mostrar_lista(ctx, mes: str, pagina: int = 1):
    """Mostra a lista de compras com paginação e botões"""
    await ctx.message.delete()
    await mostrar_lista_pagina(ctx, mes, pagina)

@bot.command(name='limpar')
async def limpar_lista(ctx, categoria: str, mes: str):
    """Limpa toda uma lista específica"""
    chave = f"{categoria.lower()}_{mes.lower()}"
    
    if chave not in listas:
        await ctx.send(embed=discord.Embed(
            description=MESSAGES['empty_list'],
            color=COLORS['error']
        ))
        return

    embed = discord.Embed(
        title="⚠️ Confirmação",
        description=f"Você tem certeza que deseja limpar toda a lista de {categoria.capitalize()} - {mes.capitalize()}?",
        color=COLORS['error']
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        if str(reaction.emoji) == "✅":
            listas[chave] = []
            listas[f"{chave}_modificado"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            salvar()
            
            await msg.edit(embed=discord.Embed(
                description=f"✅ Lista de {categoria.capitalize()} - {mes.capitalize()} foi limpa!",
                color=COLORS['success']
            ))
        else:
            await msg.edit(embed=discord.Embed(
                description="❌ Operação cancelada.",
                color=COLORS['error']
            ))
    except TimeoutError:
        await msg.edit(embed=discord.Embed(
            description="⏰ Tempo esgotado. Operação cancelada.",
            color=COLORS['error']
        ))

@bot.command(name='editar')
async def editar_item(ctx, categoria: str, mes: str, indice: int, *, novo_item: str):
    """Edita um item específico da lista"""
    chave = f"{categoria.lower()}_{mes.lower()}"
    
    if chave not in listas or not listas[chave]:
        await ctx.send(embed=discord.Embed(
            description=MESSAGES['empty_list'],
            color=COLORS['error']
        ))
        return

    if 1 <= indice <= len(listas[chave]):
        item_antigo = listas[chave][indice - 1]
        listas[chave][indice - 1] = novo_item
        listas[f"{chave}_modificado"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        salvar()

        embed = discord.Embed(
            title="✏️ Item Editado",
            description=(
                f"📋 **Lista:** {categoria.capitalize()} - {mes.capitalize()}\n"
                f"❌ **Item antigo:** `{item_antigo}`\n"
                f"✅ **Novo item:** `{novo_item}`\n"
                f"🕒 **Atualizado em:** {listas[f'{chave}_modificado']}"
            ),
            color=COLORS['success']
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(
            description="❌ Índice inválido!",
            color=COLORS['error']
        ))

@bot.command(name='ajuda')
async def ajuda(ctx):
    """Mostra a lista de comandos disponíveis"""
    embed = discord.Embed(
        title="📚 Lista de Comandos",
        description="Aqui estão todos os comandos disponíveis:",
        color=COLORS['info']
    )
    
    comandos = {
        f"{PREFIX}add": "Adiciona um item à lista\n`!add categoria mes item`\nExemplo: `!add compras janeiro 2 pães $5.50 == integral`",
        f"{PREFIX}compras": "Mostra a lista de compras\n`!compras mes [pagina]`",
        f"{PREFIX}remove": "Remove um item da lista\n`!remove categoria mes item`",
        f"{PREFIX}editar": "Edita um item da lista\n`!editar categoria mes indice novo_item`",
        f"{PREFIX}limpar": "Limpa toda uma lista\n`!limpar categoria mes`",
        f"{PREFIX}ajuda": "Mostra esta mensagem de ajuda"
    }
    
    for comando, descricao in comandos.items():
        embed.add_field(name=comando, value=descricao, inline=False)
    
    await ctx.send(embed=embed)

bot.run(TOKEN)
