import asyncio
import logging
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from textprovider.models import Coordinates, Notams, ParsedNotams
from .notamtoolkit import NotamParser, convert_time_standard, NotamScraper


logger = logging.getLogger(__name__)

@shared_task(bind=True)
def update_saved_notams(self):
    notams : list[str] = []
    base_url : str = settings.SCRAPING_URL
    locations : list = settings.SCRAPING_LOCATIONS

    #Web scraping notams
    try:
        scrapper = NotamScraper(base_url, locations)
        notams = asyncio.run(scrapper.scrap_notams())
    except Exception as error:
        logger.critical('Failed in web scraping notams')
        raise error

    notam_objects = []
    parsed_notam_objects = []
    coordinate_objects = []
    
    notam_parser = NotamParser()

    #Saving notams in db
    stripped_notams = {notam.strip() for notam in notams}
    for notam_text in stripped_notams:
        try:
            part = notam_parser.get_part(notam_text)
        except Exception as error:
            logger.warning(f'Parsing process failed when getting part: {error}')
            continue

        notam = Notams(notam_text = notam_text, part=part )
        notam_objects.append(notam)
    try:
        Notams.objects.bulk_create(notam_objects, ignore_conflicts=True)
    except Exception as error:
        logger.critical(f'Exception occurred when saving in Notams : {error}')
        raise error

    #clearing outdated notams
    cleared = []
    treshold = timezone.now()-timezone.timedelta(hours=2)
    required_clearing_fields = ('id','notam_text','part')
    notams_in_db = Notams.objects.select_related('parsed_notams').filter(parsed_notams__created__lt=treshold).only(*required_clearing_fields).values(*required_clearing_fields)
    for notam in notams_in_db:
        if notam['notam_text'] not in stripped_notams:
            Notams.objects.filter(pk=notam['id']).delete()
            cleared.append(notam['part'])
    logger.info(f'{cleared=}')


    with transaction.atomic():
        #Saving parsed notams
        not_parsed_notams = Notams.objects.filter(parsed_notams__isnull=True)
        for not_parsed_notam in not_parsed_notams:
            try:
                parsed = notam_parser.get_full_parse(not_parsed_notam.notam_text)
            except Exception as error:
                logger.warning(f'Parsing process failed when using "notam_parser" :\tid = {not_parsed_notam.part}\n{error}')
                continue      
            parsed_notam_obj = ParsedNotams(
                                    notam = not_parsed_notam,
                                    identifier = parsed['identifier'],
                                    sec_q = parsed['Q'],
                                    sec_a = parsed['A'],
                                    sec_b = parsed['B'],
                                    sec_c = parsed['C'],
                                    sec_d = parsed['D'],
                                    sec_e = parsed['E'],
                                    sec_f = parsed['F'],
                                    created = timezone.make_aware(convert_time_standard(parsed['CREATED'])),
                                    source = parsed['SOURCE']
                                    )
            parsed_notam_objects.append(parsed_notam_obj)
            
            #Saving coordinates related to notams
            coordinates = parsed['coordinates']
            for raw_coordinate in coordinates:
                coordinate = Coordinates(
                                    notam = not_parsed_notam,
                                    latitude = raw_coordinate[0],
                                    longitude = raw_coordinate[1]
                                    )
                coordinate_objects.append(coordinate)
        logger.info(f'parsed notams to be saved : {len(parsed_notam_objects)}')
        logger.info(f'coordinates to be saved : {len(coordinate_objects)}')
        try:
            ParsedNotams.objects.bulk_create(parsed_notam_objects, ignore_conflicts=True)
            Coordinates.objects.bulk_create(coordinate_objects, ignore_conflicts=True)
        except Exception as error:
            logger.error(f'Exception occurred when saving parsed_notams or coordinates : {error}')
