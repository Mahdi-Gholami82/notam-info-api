import logging
import re
import aiohttp
import asyncio
from datetime import datetime
from decimal import Decimal
from bs4 import BeautifulSoup
from requests import get

logger = logging.getLogger(__name__)

def dms_to_dd(dms):

    direction = dms[-1]
    dms_fx = str(float(dms[:-1]))

    degrees = Decimal(dms_fx[:2])
    minutes = Decimal(dms_fx[2:4])
    seconds = Decimal(dms_fx[4:])

    decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)

    if direction in ['W', 'S']:
        return -decimal_degrees
    return decimal_degrees

class NotamParser:
    def _match_subject(self, notam : str):
        notam = notam.strip()  
        parsed_notam = dict()
        pattern = r'''
            (?P<identifier>(?:[\w\s]*\/?)+)(?=[QABCDEFG]\))
            (?:Q\)(?P<Q>.+?))?
            (?:A\)(?P<A>.+?))?
            (?:B\)(?P<B>.+?))?
            (?:C\)(?P<C>.+?))?
            (?:D\)(?P<D>.+?))?
            (?:E\)(?P<E>.+?))
            (?:F\)(?P<F>.+?))?
            (?:G\)(?P<G>.+?))?
            CREATED:(?P<CREATED>.+)
            SOURCE:(?P<SOURCE>.+)
        '''
        prog : re.Pattern = re.compile(pattern=pattern,flags=re.DOTALL | re.VERBOSE)
        match = prog.match(notam)
        if not match:
            raise ValueError('Parsing failed or Notam invalid!')
        return match

    def _match_coordinates(self, notam : str):
        coordinates = re.findall(r'(\d[\d\.]{5,10}[NS]).*?(\d[\d\.]{5,10}[EW])', notam, re.DOTALL)
        coordinates = [(dms_to_dd(lat),dms_to_dd(long)) for lat,long in coordinates]
        return coordinates

    
    def get_part(self, notam : str):
        match = self._match_subject(notam)
        match_tuple = match.group('identifier','A')
        match_tuple = (match.strip() if isinstance(match,str) else '' for match in match_tuple)
        return ' '.join(match_tuple)
    
    def get_full_parse(self, notam : str):
        match = self._match_subject(notam)
        parsed_notam = {k:v.strip() if isinstance(v,str) else '' for k,v in match.groupdict().items()}
        parsed_notam['coordinates'] = self._match_coordinates(notam)
        return parsed_notam
    

class NotamScraper:
    def __init__(self, base_link, locations):
        self.base_link = base_link
        self.locations = locations

    def _soup_find_notams(self, html_text, url):
        soup = BeautifulSoup(html_text,'lxml')

        notams = soup.find_all(
                        'td',
                        class_="textBlack12",
                        valign="top",
                        width=None
                        )
        find_non = soup.find(
                        'td',
                        class_="textRed12",
                        align=None,
                        height=None
                        )
        if find_non:
            number_of_notams = int(re.search(r'Number of NOTAMs:\s*?(\d+)',find_non.text).group(1))
        else :
            raise AttributeError(f'Failed to verify the number of Notams! \n{url}')
        
        logger.info(f'Number of scrapped notams : {number_of_notams}')
        

        if number_of_notams != len(notams):
            raise ValueError('Failed to scrap all the Notams.')
        notam_texts = [notam.text for notam in notams]
        return notam_texts

    async def _fetch(self, client : aiohttp.ClientSession, link : str):
        async with client.get(url=link) as response:
            return await response.text(), response.url
        
    async def scrap_notams(self):
        tasks = []
        async with aiohttp.ClientSession() as client:
            tasks = [self._fetch(client, self.base_link.format(LOCATION_ID=location)) for location in self.locations]
            responses = await asyncio.gather(*tasks)
        soup_results = [self._soup_find_notams(*response) for response in responses]
        return sum(soup_results,[])


def convert_time_standard(time : str):
    time_format = r"%d %b %Y %H:%M:%S"
    time_obj = datetime.strptime(time.strip(),time_format)
    return time_obj

