"""Real socket tests: chunking, errors and no retry after an ambiguous response."""

import io
import json
import socket
import sys
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/blender/scripts"))
import blender as B


class ClientTests(unittest.TestCase):
    def serve(self, response, delay=0, chunks=False):
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        received = []

        def worker():
            with listener:
                with listener.accept()[0] as conn:
                    received.append(json.loads(conn.recv(65536)))
                    time.sleep(delay)
                    try:
                        if chunks:
                            for byte in response:
                                conn.sendall(bytes([byte]))
                        else:
                            conn.sendall(response)
                    except OSError:
                        pass

        thread = threading.Thread(target=worker)
        thread.start()
        self.addCleanup(thread.join)
        return port, received

    def test_chunked_unicode(self):
        wire = json.dumps(
            {"status": "success", "result": {"name": "éclair"}}, ensure_ascii=False
        ).encode()
        port, received = self.serve(wire, chunks=True)
        self.assertEqual(
            B.call("get_object_info", port=port, name="éclair"), {"name": "éclair"}
        )
        self.assertEqual(
            received, [{"type": "get_object_info", "params": {"name": "éclair"}}]
        )

    def test_reported_error(self):
        port, _ = self.serve(b'{"status":"error","message":"wrong mode"}')
        with self.assertRaisesRegex(B.BlenderError, "wrong mode"):
            B.call("execute_code", port=port, code="bad")

    def test_python_traceback_remains_readable(self):
        detail = json.dumps(
            {
                "exception_type": "ValueError",
                "message": "bad input",
                "traceback": "line 7\nValueError: bad input",
            }
        )
        port, _ = self.serve(
            json.dumps({"status": "error", "message": detail}).encode()
        )
        with self.assertRaisesRegex(B.BlenderError, "line 7\nValueError: bad input"):
            B.call("execute_code", port=port, code="bad")

    def test_nested_handler_error(self):
        port, _ = self.serve(b'{"status":"success","result":{"error":"no camera"}}')
        with self.assertRaisesRegex(B.BlenderError, "no camera"):
            B.call("render", port=port)

    def test_timeout_does_not_repeat_write(self):
        port, received = self.serve(b"{}", delay=0.15)
        with self.assertRaises(B.OutcomeUnknown):
            B.call("execute_code", port=port, timeout=0.05, code="create_object()")
        self.assertEqual(len(received), 1)

    def test_incomplete_response_is_unknown(self):
        port, _ = self.serve(b'{"status":')
        with self.assertRaises(B.OutcomeUnknown):
            B.call("execute_code", port=port, code="x=1")

    def test_saved_script_entrypoint_and_parameters(self):
        root = Path(__file__).resolve().parents[3] / "tmp"
        root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            script = Path(directory) / "script.py"
            script.write_text(
                "if __name__ == '__main__':\n    print(PARAMS['value'])\n    print(__file__)\n"
            )

            def execute_locally(code, **kwargs):
                output = io.StringIO()
                with redirect_stdout(output):
                    exec(code, {})
                return output.getvalue()

            with patch.object(B, "execute", side_effect=execute_locally):
                self.assertEqual(
                    B.run_script(script, {"value": "works"}), f"works\n{script}\n"
                )


if __name__ == "__main__":
    unittest.main()
