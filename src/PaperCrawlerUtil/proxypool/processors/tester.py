import asyncio
import time

import aiohttp
from loguru import logger

import PaperCrawlerUtil.global_val as global_val
from PaperCrawlerUtil.proxypool.schemas import Proxy
from PaperCrawlerUtil.proxypool.storages.redis import RedisClient
from aiohttp import ClientProxyConnectionError, ServerDisconnectedError, ClientOSError, ClientHttpProxyError
from asyncio import TimeoutError
from PaperCrawlerUtil.constant import *
from PaperCrawlerUtil.proxypool.storages.proxy_dict import ProxyDict

EXCEPTIONS = (
    ClientProxyConnectionError,
    ConnectionRefusedError,
    TimeoutError,
    ServerDisconnectedError,
    ClientOSError,
    ClientHttpProxyError,
    AssertionError
)


class Tester(object):
    """
    tester for testing proxies in queue
    """
    
    def __init__(self, redis_host, redis_port, redis_password, redis_database, storage="redis", need_log=True):
        """
        init redis
        """
        if storage == STORAGE_REDIS:
            self.conn = RedisClient(host=redis_host, port=redis_port, password=redis_password, db=redis_database)
        else:
            self.conn = ProxyDict()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = asyncio.get_event_loop()
        self.need_log = need_log
        self.test_batch = global_val.get_value(TEST_BATCH_NUM)
    
    async def test(self, proxy: Proxy):
        """
        test single proxy
        :param proxy: Proxy object
        :return:
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                if self.need_log:
                    logger.debug(f'testing {proxy.string()}')
                # if TEST_ANONYMOUS is True, make sure that
                # the proxy has the effect of hiding the real IP
                if global_val.get_value(TEST_ANONYMOUS):
                    url = 'https://httpbin.org/ip'
                    async with session.get(url, timeout=global_val.get_value(TESTER_TIMEOUT)) as response:
                        resp_json = await response.json()
                        origin_ip = resp_json['origin']
                    async with session.get(url, proxy=f'http://{proxy.string()}',
                                           timeout=global_val.get_value(TESTER_TIMEOUT)) as response:
                        resp_json = await response.json()
                        anonymous_ip = resp_json['origin']
                    assert origin_ip != anonymous_ip
                    assert proxy.host == anonymous_ip
                async with session.get(global_val.get_value(TESTER_URL), proxy=f'http://{proxy.string()}',
                                       timeout=global_val.get_value(TESTER_TIMEOUT),
                                       allow_redirects=False) as response:
                    if response.status in global_val.get_value(TEST_VALID_STATUS):
                        self.conn.max(proxy)
                        if self.need_log:
                            logger.debug(f'proxy {proxy.string()} is valid, set max score')
                    else:
                        self.conn.decrease(proxy)
                        if self.need_log:
                            logger.debug(f'proxy {proxy.string()} is invalid, decrease score')
            except EXCEPTIONS:
                self.conn.decrease(proxy)
                if self.need_log:
                    logger.debug(f'proxy {proxy.string()} is invalid, decrease score')
    
    @logger.catch
    def run(self):
        """
        test main method
        :return:
        """
        # event loop of aiohttp
        logger.info('stating tester...')
        count = self.conn.count()
        if self.need_log:
            logger.debug(f'{count} proxies to test')
        cursor = 0
        while True:
            if self.need_log:
                logger.debug(f'testing proxies use cursor {cursor}, count {self.test_batch}')
            cursor, proxies = self.conn.batch(cursor, count=self.test_batch)
            if proxies:
                tasks = [self.test(proxy) for proxy in proxies]
                self.loop.run_until_complete(asyncio.wait(tasks))
            if len(proxies) == 0 and cursor == 0:
                if self.need_log:
                    print("代理池无连接，等待再次测试")
                break
            if len(proxies) == 0 and cursor > 0:
                if self.need_log:
                    print("测试完代理池所有连接， 等待再次测试")
                break


def run_tester():
    host = '96.113.165.182'
    port = '3128'
    tasks = [tester.test(Proxy(host=host, port=port))]
    tester.loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    tester = Tester()
    tester.run()
    # run_tester()

