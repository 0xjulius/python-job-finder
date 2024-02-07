from bs4 import BeautifulSoup
from typing import Final
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from dotenv import load_dotenv  # Import load_dotenv
import os  # Import os module

# Load environment variables from .env file
load_dotenv()

# Telegram Bot API Token
TOKEN: Final = os.getenv('TOKEN')
BOT_USERNAME: Final = '@tyonhaku_bot'

# Command Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Moi, Tervetuloa bottiin. Oletko valmis hakemaan töitä?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olen työhakubotti, kirjoita jotain, jotta voin vastata Sinulle!")

# Response Handler
def handle_response(update: Update, text: str) -> str:
    processed: str = text.lower()

    if 'kyllä' in processed:
        return "Tässä on lista viimeisimmistä IT-työpaikoista:"
    elif 'en' in processed:
        return "Niin arvelinkin."
    else:
        return "En ymmärrä. Vastaa kyllä tai en."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(update, new_text)  # Passing update to handle_response
            await update.message.reply_text(response)
            if 'kyllä' in new_text.lower():
                await scrape_and_send_jobs(update)
        else:
            return
    else:
        response: str = handle_response(update, text)  # Passing update to handle_response
        await update.message.reply_text(response)
        if 'kyllä' in text.lower():
            await scrape_and_send_jobs(update)

# Scrape and Send Jobs
async def scrape_and_send_jobs(update: Update):
    await scrape_duunitori_jobs(update)
    await scrape_monster_jobs(update)

async def scrape_duunitori_jobs(update: Update):
    url = "https://duunitori.fi/tyopaikat?alue=vaasa&haku=it&order_by=date_posted"
    base_url = "https://duunitori.fi"
    company_name = "Duunitori.fi"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    jobs = soup.find_all('div', class_='grid grid--middle job-box job-box--lg')

    for job in jobs:
        company_name = job.find('h3', class_='job-box__title').text
        date = job.find('span', class_='job-box__job-posted').text
        location = job.find('span', class_='job-box__job-location').text
        job_url = base_url + job.a['href']

        message = (
            f"{company_name}\n"
            f"Työtehtävän nimi: {company_name}\n"
            f"Sijainti: {location.strip()} {date.strip()}\n"
            f'Linkki: {job_url}'
        )
        await update.message.reply_text(message)

async def scrape_monster_jobs(update: Update):
    url = "https://www.monster.fi/tyopaikat/it?search=&job_geo_location=Vaasa%2C+Suomi&radius=50&Etsi+ty%C3%B6paikkoja=Etsi+ty%C3%B6paikkoja&lat=63.09508899999999&lon=21.6164564&country=Suomi&administrative_area_level_1=undefined"
    base_url = "https://monster.fi"
    company_name = "Monster.fi"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    jobs = soup.find_all('div', class_='job__content clearfix')
    available_jobs = soup.find('div', class_='recruiter-seo-search-content-header')
    results = available_jobs.find('h1', class_='search-result-header').text

    message = (
        f"{company_name} - {results}\n"
        "Listataan työpaikat..\n"
    )
    await update.message.reply_text(message)

    for job in jobs:
        actual_name = job.find('span', class_='recruiter-company-profile-job-organization').text
        company_name = job.find('h2', class_='node__title').text
        date = job.find('span', class_='date').text
        location = job.find('div', class_='location').text
        job_url = job.a['href']

        message = (
            f"{actual_name}\n"
            f"Työpaikan nimi: {actual_name.strip()}\n"
            f"Työtehtävän nimi: {company_name.strip()}\n"
            f"Sijainti: {location.strip()} {date.strip()}\n"
            f'Linkki: {job_url}'
        )
        await update.message.reply_text(message)

# Error Handler
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
