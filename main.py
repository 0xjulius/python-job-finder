from bs4 import BeautifulSoup
from typing import Final
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot API Token
TOKEN: Final = os.getenv('TOKEN')
BOT_USERNAME: Final = '@tyonhaku_bot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = "Moi, Tervetuloa bottiin. Valitse kaupunki, josta haluat etsiä IT-työpaikkoja:\n" \
                   "1. Vaasa\n" \
                   "2. Tampere\n" \
                   "3. Helsinki\n"\
                   "4. Koko Suomi"
    await update.message.reply_text(message_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olen työhakubotti, kirjoita jotain, jotta voin vastata Sinulle!")

async def handle_response(update: Update, text: str) -> str:
    processed: str = text.lower()

    if 'kyllä' in processed:
        return "Tässä on lista viimeisimmistä IT-työpaikoista:"
    elif 'en' in processed:
        return "Niin arvelinkin."
    elif processed in ['1', '2', '3', '4']:
        city = await get_city(processed)
        await scrape_and_send_jobs(update, city)
    else:
        return "En ymmärrä. Valitse yksi annetuista vaihtoehdoista."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = await handle_response(update, new_text)  # Passing update to handle_response
            await update.message.reply_text(response)
            if 'kyllä' in new_text.lower():
                await scrape_and_send_jobs(update)
        else:
            return
    else:
        response: str = await handle_response(update, text)  # Passing update to handle_response
        await update.message.reply_text(response)
        if 'kyllä' in text.lower():
            await scrape_and_send_jobs(update)

async def get_city(city_number: str) -> str:
    cities = {
        '1': 'vaasa',
        '2': 'tampere',
        '3': 'helsinki',
        '4': 'koko Suomi'
    }
    return cities.get(city_number)

async def scrape_and_send_jobs(update: Update, city: str):
    city_urls = {
        'vaasa': "https://duunitori.fi/tyopaikat?haku=it-ala&alue=vaasa&filter_work_type=full_time&filter_work_relation=permanent",
        'tampere': "https://duunitori.fi/tyopaikat?alue=tampere&haku=it-ala&filter_work_relation=permanent&filter_work_type=full_time",
        'helsinki': "https://duunitori.fi/tyopaikat?alue=helsinki&haku=it-ala&filter_work_relation=permanent&filter_work_type=full_time",
        'koko Suomi': "https://duunitori.fi/tyopaikat?haku=it-ala&filter_work_relation=permanent&filter_work_type=full_time"
    }
    await scrape_jobs(update, city_urls[city], city)

async def scrape_jobs(update: Update, url: str, city: str):
    base_url = "https://duunitori.fi"
    company_name = "Duunitori.fi"

    current_page = 1
    max_pages = 3

    while current_page <= max_pages:
        response = requests.get(f"{url}&sivu={current_page}")
        soup = BeautifulSoup(response.text, 'lxml')
        jobs = soup.find_all('div', class_='grid grid--middle job-box job-box--lg')

        job_count = len(jobs)
        message_header = f"Hakusi '{city.capitalize()}' IT-työpaikoista tuotti {job_count} tulosta.\n\n"

        # Split message into chunks to avoid "Message is too long" error
        message_chunks = [message_header]
        for job in jobs:
            company_name = job.find('h3', class_='job-box__title').text
            date = job.find('span', class_='job-box__job-posted').text
            location = job.find('span', class_='job-box__job-location').text
            job_url = base_url + job.a['href']

            message = (
                f"{company_name}\n"
                f"Työtehtävän nimi: {company_name}\n"
                f"Sijainti: {location.strip()} {date.strip()}\n"
                f'Linkki: {job_url}\n\n'
            )
            # Check if adding the current job will exceed message length limit
            if len(message_chunks[-1]) + len(message) > 4096:
                message_chunks.append(message)
            else:
                message_chunks[-1] += message

        # Send each chunk of the message separately
        for chunk in message_chunks:
            await update.message.reply_text(chunk)

        current_page += 1

        await asyncio.sleep(1)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')  # Corrected here

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    print('Ladataan..')
    app.run_polling(poll_interval=5)
