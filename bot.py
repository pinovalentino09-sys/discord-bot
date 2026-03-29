import discord
from discord.ext import commands
import json
import os

TOKEN = "PON_AQUI_TU_TOKEN_NUEVO"

CANAL_PRUEBAS = "├『📄』allys-proff"
CANAL_CONTADOR = "├『🕹️』allys-count"
ROL_ADMIN = "Admin"   # cambia al nombre del rol que podrá usar h!reset

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="h!", intents=intents)

# cargar datos
def cargar_datos():
    if os.path.exists("datos.json"):
        with open("datos.json", "r") as f:
            return json.load(f)
    return {}

def guardar_datos():
    with open("datos.json", "w") as f:
        json.dump(contador_alianzas, f)

contador_alianzas = cargar_datos()
mensaje_contador_id = None


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


@bot.event
async def on_message(message):
    global mensaje_contador_id

    if message.author.bot:
        return

    if message.channel.name != CANAL_PRUEBAS:
        await bot.process_commands(message)
        return

    # contar imágenes del mensaje
    imagenes_validas = 0
    for archivo in message.attachments:
        if archivo.filename.lower().endswith(("png", "jpg", "jpeg", "gif", "webp")):
            imagenes_validas += 1

    if imagenes_validas == 0:
        await bot.process_commands(message)
        return

    usuario = str(message.author)

    if usuario not in contador_alianzas:
        contador_alianzas[usuario] = 0

    contador_alianzas[usuario] += imagenes_validas
    guardar_datos()

    canal_contador = discord.utils.get(bot.get_all_channels(), name=CANAL_CONTADOR)

    if canal_contador is None:
        return

    # crear texto ranking
    ranking = sorted(contador_alianzas.items(), key=lambda x: x[1], reverse=True)
    texto = "🏆 **CONTEO DE ALIANZAS** 🏆\n\n"

    for user, cantidad in ranking:
        texto += f"**{user}** → {cantidad} pruebas\n"

    # editar mensaje existente
    if mensaje_contador_id:
        try:
            mensaje = await canal_contador.fetch_message(mensaje_contador_id)
            await mensaje.edit(content=texto)
        except:
            mensaje = await canal_contador.send(texto)
            mensaje_contador_id = mensaje.id
    else:
        mensaje = await canal_contador.send(texto)
        mensaje_contador_id = mensaje.id

    await bot.process_commands(message)


# COMANDO TOP
@bot.command()
async def top(ctx):
    ranking = sorted(contador_alianzas.items(), key=lambda x: x[1], reverse=True)

    embed = discord.Embed(
        title="🏆 Top Alianzas",
        color=discord.Color.gold()
    )

    for user, cantidad in ranking[:10]:
        embed.add_field(name=user, value=f"{cantidad} pruebas", inline=False)

    await ctx.send(embed=embed)


# COMANDO RESET (solo rol)
@bot.command()
async def reset(ctx):
    if ROL_ADMIN not in [rol.name for rol in ctx.author.roles]:
        await ctx.send("❌ No tienes permiso para usar este comando.")
        return

    contador_alianzas.clear()
    guardar_datos()
    await ctx.send("🧹 Contador reseteado correctamente.")


bot.run("DISCORD_TOKEN")
