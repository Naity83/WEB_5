import aiohttp
import asyncio
import platform
import sys
from datetime import timedelta, datetime

class HttpError(Exception):
    pass

async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    raise HttpError(f"Error status: {resp.status} for {url}")
        except (aiohttp.ClientConnectorError, aiohttp.InvalidURL) as err:
            raise HttpError(f'Connection error: {url}', str(err))

async def day(index_day):
    if index_day < 11:
        delta = datetime.now() - timedelta(days=index_day)
        return delta.strftime('%d.%m.%Y')
    else:
        return None  # Returning None for index_day >= 11

async def parser(response_list, additional_currencies):
    new_list = []
    for response in response_list:
        currency_dict = {}
        for item in response['exchangeRate']:
            if item['currency'] in additional_currencies:
                currency_dict[item['currency']] = {'sale': item['saleRateNB'], 'purchase': item['purchaseRateNB']}
            elif item['currency'] == 'EUR':
                currency_dict['EUR'] = {'sale': item['saleRateNB'], 'purchase': item['purchaseRateNB']}
            elif item['currency'] == 'USD':
                currency_dict['USD'] = {'sale': item['saleRateNB'], 'purchase': item['purchaseRateNB']}
        new_dict = {response['date']: currency_dict}
        new_list.append(new_dict)
    return new_list

async def main():
    index_day = int(sys.argv[1])
    additional_currencies = sys.argv[2:]
    response_list = []
    try:
        initial_date = await day(index_day)
        if initial_date is None:
            raise HttpError("Invalid index_day value. Please enter a value less than 11.")
        
        while index_day >= 1:
            response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={initial_date}')
            response_list.append(response)
            index_day -= 1
            initial_date = await day(index_day)  # Update initial_date for the next iteration
    except HttpError as err:
        print(err)
        return None
          
    return await parser(response_list, additional_currencies)

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main())
    print(r)