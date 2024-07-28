import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Token del bot
TOKEN = '7016257874:AAELcy64yU5QzD-8fWpiuxQ0cT-EnkZZiF0'

# Cargar las bases de datos
df1 = pd.read_csv('base_datos.csv')  # Primera base de datos
df2 = pd.read_csv('base_datos_2.csv')  # Segunda base de datos

# Convertir todos los valores de las columnas 'Codigo', 'ID', y 'Nombre del emplazamiento' a minúsculas para una búsqueda no sensible a mayúsculas y minúsculas
df1['Codigo'] = df1['Codigo'].str.lower()
df1['ID'] = df1['ID'].astype(str).str.lower()
df2['ID'] = df2['ID'].astype(str).str.lower()
df1['Nombre del emplazamiento'] = df1['Nombre del emplazamiento'].str.lower()  # Convertir también a minúsculas para la búsqueda por aproximación

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hola! Envíame un código estilo "ARBA0001", un ID usando el comando /lookup, o parte de un nombre y te devolveré la información correspondiente.')

def generate_image(result):
    fig, ax = plt.subplots(figsize=(12, 1))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=result.values, colLabels=result.columns, cellLoc='center', loc='center', edges='horizontal')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    col_widths = [max(len(str(val)) for val in result[col]) for col in result.columns]
    for i, width in enumerate(col_widths):
        table.auto_set_column_width([i])
    table.scale(1.2, 1.2)
    plt.savefig('/home/knuxo/lookupanexo/result_table.png', bbox_inches='tight')

def format_text_result(result):
    formatted_text = []
    for _, row in result.iterrows():
        formatted_text.append(
            f"Emplazamiento: {row['Codigo'].upper()}\n"
            f"ID: {row['ID'].upper()}\n"  # Convertir ID a mayúsculas
            f"Nombre: {row['Nombre del emplazamiento']}\n"
            f"Direccion: {row['Direccion']}\n"
            f"Municipio: {row['Municipio']}\n"
            f"Localidad: {row['Localidad']}\n"
            f"Provincia: {row['Provincia']}\n"
            f"Latitud: {row['Latitud']}\n"
            f"Longitud: {row['Longitud']}\n"
            f"Categoria: {row['Categoria'].upper()}"
        )
    return "\n".join(formatted_text)

async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args  # Obtener los argumentos del comando
    if len(args) == 0:
        await update.message.reply_text('Por favor, proporciona un código, un ID o parte de un nombre después del comando /lookup.')
        return

    search_term = args[0].strip().lower()  # Convertir el término de búsqueda a minúsculas
    print(f"Realizando búsqueda para: {search_term}")

    # Buscar por Código en la primera base de datos
    result = df1[df1['Codigo'] == search_term]

    # Si no se encuentra, buscar por ID en la segunda base de datos
    if result.empty:
        print("No encontrado en base_datos.csv, buscando en base_datos_2.csv...")
        result = df2[df2['ID'] == search_term]

    # Si no se encuentra, buscar por aproximación en la columna 'Nombre del emplazamiento'
    if result.empty:
        print("No encontrado en base_datos_2.csv, buscando por aproximación en 'Nombre del emplazamiento'...")
        result = df1[df1['Nombre del emplazamiento'].str.contains(search_term)]

    if not result.empty:
        print("Resultado encontrado, generando imagen...")
        generate_image(result)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('/home/knuxo/lookupanexo/result_table.png', 'rb'))
        await update.message.reply_text(
            'Estos son los sitios que arrojó tu búsqueda. En caso de querer el detalle de algun sitio en específico, repite la búsqueda con el *Emplazamiento* o *ID*.',
            parse_mode='Markdown'
        )
        print("Imagen y mensaje enviados.")
        return

    if result.empty:
        print("Código, ID o nombre no encontrado.")
        await update.message.reply_text('Código, ID o nombre no encontrado.')
    else:
        print("Resultado encontrado, generando imagen...")
        generate_image(result)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('/home/knuxo/lookupanexo/result_table.png', 'rb'))
        text_result = format_text_result(result)
        await update.message.reply_text(text_result)
        print("Resultado enviado.")

def main():
    print("Iniciando el bot...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("lookup", lookup))

    print("Bot iniciado y esperando mensajes...")
    application.run_polling()

if __name__ == '__main__':
    main()