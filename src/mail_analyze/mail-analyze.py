import imaplib
from email.header import decode_header
from collections import Counter
import concurrent.futures
import logging
import sys
import multiprocessing
import config

logger = logging.getLogger(__name__)


logging.basicConfig(filename='myapp.log', level=logging.INFO)
logger.info('Started')

M = imaplib.IMAP4_SSL(host='imap.gmail.com')

login_status, _ = M.login(config.username, config.password)
logger.info("Login Status %s", login_status)

select_status, _ = M.select()
M.select('"[Gmail]/All Mail"')
logger.info("Mailbox Selection %s", select_status)

typ, data = M.search(None, 'ALL')
data = data[0].split()
logger.info("Mailbox Search %s, found %d messages.", typ, len(data))

def processData(num, list):

    try:

        status, response = M.fetch(num, 'BODY.PEEK[HEADER.FIELDS (FROM)]')
        logger.info(f'Fetch %s | Content: %s | Sender: %s' % (status, response[0], response[0][1]))
        list.append(response[0][1])
    except Exception as e:
        logger.error("Exception while running thread: %s", sys.exc_info(e))
        raise

def test():
    
    manager = multiprocessing.Manager()
    senders_list = manager.list()
    
    executor = concurrent.futures.ProcessPoolExecutor(8)
    futures = [executor.submit(processData, num, senders_list) for num in data]
    concurrent.futures.wait(futures)

    logger.info('Final list has %d items. Content: %s\n', len(senders_list), senders_list)

    for sender, count in Counter(senders_list).most_common(5):
        print(f'{sender}, {count}\n')


    close_status, _ =M.close()
    logger.info('Closed status %s', close_status)

    logout_status, _ = M.logout()
    logger.info('Logout status %s', logout_status)

if __name__ == '__main__':
    test()