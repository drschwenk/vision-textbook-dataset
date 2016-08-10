import requests
import os.path
from lxml import html
from ai2.vision.utils.io import logger


def download_quizzes(topic, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    concepts = get_concepts(topic)
    logger.info('%d concepts present in topic %s', len(concepts), topic)
    for c in concepts:
        quizzes = get_quizzes(c)
        logger.info('%d quizzes present in concept %s', len(quizzes), c)
        for q in quizzes:
            download_quiz(output_dir, q)


def get_concepts(topic):
    res = requests.get('http://www.ck12.org/%s/' % topic)
    res.raise_for_status()
    content = res.content
    tree = html.fromstring(content)
    concepts = []
    for e in tree.xpath('//li[@class="concepts"]/a'):
        concepts.append(e.attrib['href'].split('/')[-2])
    return concepts


def get_quizzes(concept):
    quizzes = []
    url = 'http://api-prod.ck12.org/flx/get/minimal/modalities/at%20grade/' + concept + '?pageSize=13&pageNum=0&ownedBy=ck12&modalities=concept%2Clessonplan%2Clessonplanans%2Csimulationint%2Clessonplanx%2Crubric%2Cactivityans%2Clesson%2Cpostreadans%2Cprepostread%2Cweb%2Ccthink%2Crwaans%2Csection%2Cplix%2Cwhileread%2Cquiz%2Clessonplanxans%2Cpreread%2Cattachment%2Clecture%2Cpresentation%2Cimage%2Cquizdemo%2Crwa%2Cwhilereadans%2Cprereadans%2Cpostread%2Cexerciseint%2Clab%2Cflashcard%2Cstudyguide%2Cquizans%2Casmtpractice%2Cprepostreadans%2Clabans%2Casmtquiz%2Cworksheet%2Chandout%2Csimulation%2Cexercise%2Cactivity%2Cworksheetans%2Caudio%2Cconceptmap%2Cenrichment%2Cinteractive&level=at%2Bgrade&expirationAge=daily'
    res = requests.get(url)
    res.raise_for_status()
    for m in res.json()['response']['domain']['modalities']:
        if m['artifactType'] == 'quiz':
            quizzes.append(m['perma'].split('/')[-1])
    return quizzes


def download_quiz(output_dir, quiz):
    filename = output_dir + '/{0}-Answer-Key.docx'.format(quiz)
    if os.path.isfile(filename):
        logger.info('Quiz: %s already exists. Skipping.', quiz)
        return

    res = requests.get('http://www.ck12.org/flx/show/answer%20key/' + quiz + '-Answer-Key')
    if res.status_code != 200:
        logger.error('Error getting quiz %s: %s',quiz, res.status_code)
        return

    res.raise_for_status()
    assert res.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    with open(filename, 'wb') as f:
        f.write(res.content)
