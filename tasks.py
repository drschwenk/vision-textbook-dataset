from invoke import task
import ai2.vision.utils as utils
from ai2.vision.utils.io import logger


@task(
    help={
        'directory': 'Directory to store the downloaded docx files',
        'topic': 'Topic to download (earth-science/life-science/physical-science/biology/chemistry/physics)'
    }
)
def download_ck12_quizzes(ctx, topic, directory):
    """Download quizzes from http://www.ck12.org/"""
    import ai2.vision.textbook_dataset.ck12.quiz
    utils.io.init_logging(log_level='debug')
    ai2.vision.textbook_dataset.ck12.quiz.download_quizzes(topic, directory)
    logger.info('Downloading quizzes completed')

@task(
    help={
        'directory': 'Directory to store the downloaded lesson pdf files',
        'topic': 'Topic to download (earth-science/life-science/physical-science/biology/chemistry/physics)'
    }
)
def download_ck12_lessons(ctx, topic, directory):
    """Download quizzes from http://www.ck12.org/"""
    import ai2.vision.textbook_dataset.ck12.lessons
    utils.io.init_logging(log_level='debug')
    ai2.vision.textbook_dataset.ck12.lessons.download_topic_lessons(topic, directory)
    logger.info('Downloading lessons completed')
