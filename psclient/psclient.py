import asyncio
import re
import socket
import sys
import time

import psclient.config as conf
import psclient.utils as utils


class _BaseClient:
    def __init__(self, host='localhost', port=9042, username=None, password=None,
                 timeout=10, recv_buffer=4096):
        """

        :param host:
        :param port:
        :param username:
        :param password:
        :param timeout:
        :param recv_buffer:
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.recv_buffer = recv_buffer
        self.server_encoding = sys.stdout.encoding

    def connect(self):
        raise NotImplemented

    def disconnect(self):
        raise NotImplemented

    def authenticate(self):
        raise NotImplemented

    def execute(self, query):
        raise NotImplemented

    def _get_login_cmd(self):
        """

        """
        return "login '{}' '{}'".format(
            self.username,
            self.password
        )

    def _set_encoding(self, data):
        """

        :param data:
        :return:
        """
        try:
            if data.startswith("#"):
                encoding = data.split(';')
                encoding = encoding[2].strip().strip('"')
            elif data.startswith("<"):
                encoding = re.search(conf.xml_encoding_regex, data).group(1)
            elif data.startswith("{"):
                encoding = re.search(conf.json_encoding_regex, data).group(1)
            else:
                raise ValueError
        except (IndexError, TypeError, ValueError) as exc:
            encoding = 'UTF8'
            utils.eprint(
                "{}: cannot determine server encoding: {}\n".format(conf.error_marker, exc),
                "using default UTF8"
            )

        encoding = encoding.upper()
        self.server_encoding = encoding

        if encoding in ["UTF8", "UNICODE"]:
            self.server_encoding = "UTF-8"
        elif encoding in ["LATIN1", "ISO88591"]:
            self.server_encoding = "ISO-8859-1"

    def _get_encoding(self):
        raise NotImplemented

    @staticmethod
    def _check_end_response(data):
        """

        :param data:
        :return:
        """
        part = len(conf.end_response_marker)
        return len(data) >= part and data[-part:].decode() == conf.end_response_marker

    @staticmethod
    def _normalize_statement(stm):
        """

        :param stm:
        """
        stm = stm.replace('\n', ' ')
        stm = stm.replace('\t', ' ')

        if not stm.endswith("\n"):
            stm += "\n"

        return stm

    def _normalize_output(self, data):
        """

        :param data:
        :return:
        """
        try:
            result = data.decode(self.server_encoding, 'replace')
        except LookupError:
            result = data.decode()

        return result[0:-len(conf.end_response_marker)]


class PSClient(_BaseClient):
    def __init__(self, host='localhost', port=9042, username=None, password=None,
                 timeout=5, recv_buffer=4096, max_reconnect=5):
        """

        :param host:
        :param port:
        :param username:
        :param password:
        :param max_reconnect:
        :param timeout:
        :param recv_buffer:
        """
        super().__init__(host, port, username, password, timeout, recv_buffer)
        self.conn = None
        self.max_reconnect = max_reconnect

    def connect(self):
        """

        """
        reconnect = True
        reconnect_count = 0

        while reconnect:
            if reconnect_count > self.max_reconnect:
                raise ConnectionError(
                    "Connection Error: reached maximum reconnect"
                ) from None

            try:
                if self.conn is None:
                    self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.conn.settimeout(self.timeout)
                    self.conn.connect((self.host, self.port))

                if self.username is not None:
                    self.authenticate()

                self._get_encoding()
                reconnect = False
            except socket.error:
                self.disconnect()
                reconnect_count += 1
                time.sleep(0.1)

    def disconnect(self):
        """

        """
        if self.conn is not None:
            self.conn.close()
        self.conn = None

    def authenticate(self):
        """

        """
        result, _ = self.execute(self._get_login_cmd())
        if 'ERROR' in result:
            raise RuntimeError(result)

    def _get_encoding(self):
        """

        """
        output, _ = self.execute(conf.encoding_query)
        self._set_encoding(output)
        return self.server_encoding

    def execute(self, query):
        """

        :param query:
        :return:
        """
        query = self._normalize_statement(query)

        end_time = 0
        buf = bytes()
        recv_buffer = 1
        first_package = True
        start_time = time.time()

        self.conn.sendall(query.encode())

        while True:
            package = self.conn.recv(recv_buffer)
            if not package:
                break

            buf += package

            if first_package:
                end_time = time.time()
                first_package = False
                recv_buffer = self.recv_buffer

            if self._check_end_response(buf):
                break

        return self._normalize_output(buf), dict(time_info=dict(
            start=start_time,
            end_exec=end_time,
            end_out=time.time()
        ))


class AIOPSClient(_BaseClient):
    def __init__(self, host='localhost', port=9042, username=None, password=None,
                 timeout=60, recv_buffer=4096):
        """

        :param host:
        :param port:
        :param username:
        :param password:
        :param timeout:
        :param recv_buffer:
        """
        super().__init__(host, port, username, password, timeout, recv_buffer)
        self._reader = None
        self._writer = None

    async def connect(self):
        """

        """
        if not (self._reader or self._writer):
            self._reader, self._writer = await asyncio.open_connection(self.host, self.port)

        if self.username is not None:
            await self.authenticate()

        await self._get_encoding()

    async def disconnect(self):
        """

        """
        self._reader = None
        if self._writer is not None:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None

    async def authenticate(self):
        """

        """
        result, _ = await self.execute(self._get_login_cmd())
        if 'ERROR' in result:
            raise RuntimeError(result)

    async def _get_encoding(self):
        """

        """
        output, _ = await self.execute(conf.encoding_query)
        self._set_encoding(output)
        return self.server_encoding

    async def execute(self, query):
        """

        :param query:
        :return:
        """
        end_time = 0
        buf = bytes()
        recv_buffer = 1
        first_package = True
        start_time = time.time()

        query = self._normalize_statement(query)
        self._writer.write(query.encode())

        while True:
            package = await self._reader.read(recv_buffer)
            if not package:
                break

            buf += package

            if first_package:
                end_time = time.time()
                first_package = False
                recv_buffer = self.recv_buffer

            if self._check_end_response(buf):
                break

        return self._normalize_output(buf), dict(time_info=dict(
            start=start_time,
            end_exec=end_time,
            end_out=time.time()
        ))


class CLIClient(PSClient):
    def __init__(self, host='localhost', port=9042, username=None, password=None,
                 timeout=5, recv_buffer=4096, max_reconnect=5, timing=True, pretty=True):
        """

        :param host:
        :param port:
        :param username:
        :param password:
        :param timeout:
        :param recv_buffer:
        :param max_reconnect:
        :param timing:
        :param pretty:
        """
        super().__init__(host, port, username, password, timeout, recv_buffer, max_reconnect)
        self.pretty = pretty
        self.timing = timing

    def get_format(self):
        """

        :return:
        """
        output, _ = self.safe_execute(conf.format_query)

        if 'JSON' in output:
            return 'JSON'
        if 'XML' in output:
            return 'XML'
        if 'ASCII' in output:
            return 'ASCII'
        return 'UNKNOWN'

    def safe_execute(self, query):
        """

        :param query:
        :return:
        """
        try:
            return self.execute(query)
        except socket.error as exc:
            utils.eprint(str(exc))
            utils.eprint("reconnecting...")

            try:
                self.connect()
                utils.eprint("successfully connected")
            except ConnectionError as exc:
                utils.eprint(str(exc))
                sys.exit(1)

            return None, None

    def dump_output(self, result, time_info=None, timing=None):
        """

        :param result:
        :param time_info:
        :param timing:
        """
        if not result:
            return

        if sys.stdout.isatty() and self.pretty is True:
            utils.pretty_print(result, arg=self.get_format())
        else:
            print(result)

        if self.timing and timing is not False:
            t = time_info['time_info']
            exec_sec = round(t['end_exec'] - t['start'], 4)
            total_sec = round(t['end_out'] - t['start'], 4)

            utils.eprint()
            utils.eprint("execution: {} sec".format(exec_sec))
            utils.eprint("total:     {} sec".format(total_sec))
