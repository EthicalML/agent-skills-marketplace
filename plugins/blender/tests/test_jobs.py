"""Exercise the real detached supervisor with a fake Blender executable."""

import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "blender" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from jobs import cancel_job, job_status, start_job  # noqa: E402


class JobsTest(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[3] / "tmp"
        root.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=root)
        self.root = Path(self.temporary.name)
        self.binary = self.root / "fake-blender"
        self.binary.write_text(
            f"#!{sys.executable}\nimport runpy, sys\nrunpy.run_path(sys.argv[-1])\n"
        )
        self.binary.chmod(0o755)
        self.blend = self.root / "scene.blend"
        self.blend.touch()
        self.script = self.root / "task.py"
        self.jobs = []

    def tearDown(self):
        for job in self.jobs:
            cancel_job(job)
            self.wait(job)
        self.temporary.cleanup()

    def start(self, code):
        self.script.write_text(code)
        status = start_job(self.blend, self.script, self.root, self.binary)
        self.jobs.append(status["job_dir"])
        return status["job_dir"]

    def wait(self, job, states=("succeeded", "failed", "cancelled")):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            status = job_status(job)
            if status["state"] in states:
                return status
            time.sleep(0.05)
        self.fail(f"Job did not reach {states}: {status}")

    def test_success_and_output_directory(self):
        job = self.start(
            "import os\nfrom pathlib import Path\nPath('result.txt').write_text(os.environ['BLENDER_JOB_DIR'])\nprint('Frame 1 complete')\n"
        )
        result = self.wait(job)
        self.assertEqual(result["state"], "succeeded")
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("Frame 1 complete", result["log_tail"])
        self.assertEqual((Path(job) / "result.txt").read_text(), job)
        self.assertEqual(cancel_job(job)["state"], "succeeded")
        self.assertFalse(cancel_job(job)["cancel_requested"])

    def test_failure(self):
        result = self.wait(self.start("raise RuntimeError('intentional failure')\n"))
        self.assertEqual(result["state"], "failed")
        self.assertNotEqual(result["exit_code"], 0)
        self.assertIn("intentional failure", result["log_tail"])

    def test_cancellation(self):
        job = self.start("import time\nprint('ready', flush=True)\ntime.sleep(60)\n")
        self.wait(job, ("running",))
        self.assertTrue(cancel_job(job)["cancel_requested"])
        self.assertEqual(self.wait(job)["state"], "cancelled")

    def test_cancellation_kills_unresponsive_child(self):
        job = self.start(
            "import signal, time\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\nprint('ready', flush=True)\ntime.sleep(60)\n"
        )
        deadline = time.monotonic() + 5
        while "ready" not in job_status(job)["log_tail"]:
            if time.monotonic() >= deadline:
                self.fail("Child did not install its signal handler")
            time.sleep(0.05)
        cancel_job(job)
        result = self.wait(job)
        self.assertEqual(result["state"], "cancelled")
        self.assertEqual(result["exit_code"], -9)

    def test_rejects_missing_input_and_relative_paths(self):
        with self.assertRaises(FileNotFoundError):
            start_job(self.blend, self.script, self.root, self.binary)
        with self.assertRaises(ValueError):
            start_job("relative.blend", self.script, self.root, self.binary)


if __name__ == "__main__":
    unittest.main()
