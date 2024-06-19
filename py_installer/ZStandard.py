import sys
import time
import subprocess
import multiprocessing

from octoeverywhere.compression import Compression

from .Util import Util
from .Logging import Logger
from .Context import Context, OsTypes

# A helper class to make sure the optional zstandard lib and deps are installed.
class ZStandard:

    # Tries to install zstandard, but this won't fail if the install fails.
    @staticmethod
    def TryToInstallZStandard(context:Context):

        # We don't even try installing on K1 or SonicPad, we know it fail.
        if context.OsType == OsTypes.K1 or context.OsType == OsTypes.SonicPad:
            return

        # We also don't try install on systems with 2 cores or less, since it's too much work and the OS most of the time
        # Can't support zstandard because there's no pre-made binary, it can't be built, and the install process will take too long.
        if multiprocessing.cpu_count() < Compression.ZStandardMinCoreCountForInstall:
            return

        # Try to install or upgrade.
        Logger.Info("Installing zstandard, this might take a moment...")
        startSec = time.time()
        (returnCode, stdOut, stdError) = Util.RunShellCommand("sudo apt-get install zstd -y", False)
        Logger.Debug(f"Zstandard apt install result. Code: {returnCode}, StdOut: {stdOut}, StdErr: {stdError}")

        # Use the same logic as we do in the Compression class.
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', Compression.ZStandardPipPackageString], timeout=60.0, check=False, capture_output=True)
        Logger.Debug(f"Zstandard PIP install result. Code: {result.returncode}, StdOut: {result.stdout}, StdErr: {result.stderr}")

        # Report the status to the installer log.
        if result.returncode == 0:
            Logger.Info(f"zStandard successfully installed/updated. It took {str(round(time.time()-startSec, 2))} seconds.")
            return

        # Tell the user, but this is a best effort, so if it fails we don't care.
        # Any user who wants to use RTSP and doesn't have ffmpeg installed can use our help docs to install it.
        Logger.Info(f"We didn't install zstandard. It took {str(round(time.time()-startSec, 2))} seconds. Output: {result.stderr}")
