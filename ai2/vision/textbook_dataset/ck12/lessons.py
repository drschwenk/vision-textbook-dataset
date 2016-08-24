import requests
import os.path
import time
from collections import defaultdict
from bs4 import BeautifulSoup
import random
from ai2.vision.utils.io import logger
from . import quiz
from . import req_cookie


def get_topic_lesson_names(concept):
    lessons = []
    url = 'http://api-prod.ck12.org/flx/get/minimal/modalities/at%20grade/' + concept + \
    '?pageSize=13&pageNum=0&ownedBy=ck12&modalities=concept%2Clessonplan%2Clessonplanans%2Csimulationint%2Clessonplanx' \
    '%2Crubric%2Cactivityans%2Clesson%2Cpostreadans%2Cprepostread%2Cweb%2Ccthink%2Crwaans%2Csection%2Cplix%2Cwhileread' \
    '%2Cquiz%2Clessonplanxans%2Cpreread%2Cattachment%2Clecture%2Cpresentation%2Cimage%2Cquizdemo%2Crwa%2Cwhilereadans' \
    '%2Cprereadans%2Cpostread%2Cexerciseint%2Clab%2Cflashcard%2Cstudyguide%2Cquizans%2Casmtpractice%2Cprepostreadans' \
    '%2Clabans%2Casmtquiz%2Cworksheet%2Chandout%2Csimulation%2Cexercise%2Cactivity%2Cworksheetans%2Caudio%2Cconceptmap' \
    '%2Cenrichment%2Cinteractive&level=at%2Bgrade&expirationAge=daily'

    res = requests.get(url)
    for m in res.json()['response']['domain']['modalities']:
        if m['artifactType'] == 'lesson':
            lessons.append(m['perma'].split('/')[-1])
    return lessons


def make_pdf_download_requests(out_dir, concept_topics):
    lesson_base_url = 'http://www.ck12.org/earth-science/{}/lesson/{}'
    render_req_base_url = 'http://www.ck12.org/render/pdf/status/{}/{}'

    topic_lessons = defaultdict(list)
    for topic in concept_topics:
        topic_lessons[topic].extend(get_topic_lesson_names(topic))
    for topic, lessons in topic_lessons.items():
        for lesson in lessons:
            out_filename = check_file_exists(out_dir, lesson)
            if not out_filename:
                continue
            lesson_url = lesson_base_url.format(topic, lesson)
            lesson_r = requests.get(lesson_url)
            soup = BeautifulSoup(lesson_r.content, 'html.parser')
            pdf_links = soup.find_all("a", {"class": "js_signinrequired pdf"})
            link_attr = pdf_links[0].attrs
            da_id = link_attr['data-artifactid']
            dar_id = link_attr['data-artifactrevisionid']
            render_req_url = render_req_base_url.format(da_id, dar_id)
            render_req_response = requests.get(render_req_url, cookies=req_cookie.your_acc_cookie).json()

            while render_req_response['status'] != 'SUCCESS':
                retry_time = 15 + random.randrange(-3, 3, 1)
                logger.info('%s pdf is %s... waiting %s before trying again', lesson, render_req_response['status'], retry_time)
                time.sleep(retry_time)
                render_req_response = requests.get(render_req_url, cookies=req_cookie.your_acc_cookie).json()

            download_uri = None
            if 'downloadUri' in render_req_response.keys():
                download_uri = render_req_response['downloadUri']
            elif render_req_response['result']:
                download_uri = render_req_response['result']
            elif not download_uri:
                logger.error('error for %s with status', lesson, render_req_response['status'])
            download_lesson_pdf(out_filename, lesson, download_uri)


def check_file_exists(output_dir, lesson_title):
    filename = output_dir + '/{}.pdf'.format(lesson_title)
    if os.path.isfile(filename):
        logger.info('lesson: %s already exists. Skipping.', lesson_title)
        return False
    else:
        return filename


def download_lesson_pdf(filename, lesson_title, pdf_uri):
    res = requests.get(pdf_uri)
    if res.status_code != 200:
        logger.error('Error getting lesson %s: %s', pdf_uri, res.status_code)
        return
    res.raise_for_status()
    assert res.headers['Content-Type'] == 'application/pdf'
    with open(filename, 'wb') as f:
        f.write(res.content)


def download_topic_lessons(topic, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    topic_concepts = quiz.get_concepts(topic)
    logger.info('%d concepts present in topic %s', len(topic_concepts), topic)
    make_pdf_download_requests(out_dir, topic_concepts[14:20])

