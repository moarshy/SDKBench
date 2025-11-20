"""Base executor for running commands in solution directories."""

import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ExecutionResult:
    """Result of a command execution."""

    def __init__(
        self,
        success: bool,
        stdout: str,
        stderr: str,
        return_code: int,
        duration: float,
        error: Optional[str] = None,
    ):
        """Initialize execution result.

        Args:
            success: Whether execution succeeded
            stdout: Standard output
            stderr: Standard error
            return_code: Process return code
            duration: Execution duration in seconds
            error: Error message if any
        """
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.duration = duration
        self.error = error

    def __repr__(self) -> str:
        """String representation."""
        status = "SUCCESS" if self.success else "FAILED"
        return f"<ExecutionResult {status} code={self.return_code} duration={self.duration:.2f}s>"


class Executor:
    """Base executor for running commands."""

    def __init__(self, working_dir: Path, timeout: int = 300):
        """Initialize executor.

        Args:
            working_dir: Directory to run commands in
            timeout: Command timeout in seconds (default: 5 minutes)
        """
        self.working_dir = Path(working_dir)
        self.timeout = timeout

    def run_command(
        self,
        command: List[str],
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        """Run a command and capture output.

        Args:
            command: Command and arguments to run
            env: Optional environment variables
            timeout: Optional timeout override

        Returns:
            ExecutionResult with command output and status
        """
        cmd_timeout = timeout or self.timeout

        try:
            start_time = time.time()

            # Run command
            process = subprocess.Popen(
                command,
                cwd=self.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=cmd_timeout)
                duration = time.time() - start_time

                return ExecutionResult(
                    success=process.returncode == 0,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=process.returncode,
                    duration=duration,
                )

            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                duration = time.time() - start_time

                return ExecutionResult(
                    success=False,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=-1,
                    duration=duration,
                    error=f"Command timed out after {cmd_timeout}s",
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                duration=0.0,
                error=f"Failed to execute command: {str(e)}",
            )

    def check_node_installed(self) -> bool:
        """Check if Node.js is installed.

        Returns:
            True if node is available
        """
        result = self.run_command(["node", "--version"], timeout=5)
        return result.success

    def check_npm_installed(self) -> bool:
        """Check if npm is installed.

        Returns:
            True if npm is available
        """
        result = self.run_command(["npm", "--version"], timeout=5)
        return result.success

    def check_dependencies_installed(self) -> bool:
        """Check if node_modules exists.

        Returns:
            True if dependencies are installed
        """
        node_modules = self.working_dir / "node_modules"
        return node_modules.exists() and node_modules.is_dir()

    def install_dependencies(self) -> ExecutionResult:
        """Install npm dependencies.

        Returns:
            ExecutionResult from npm install
        """
        return self.run_command(["npm", "install"], timeout=600)  # 10 minutes

    def get_package_scripts(self) -> Dict[str, str]:
        """Get available npm scripts from package.json.

        Returns:
            Dict mapping script names to commands
        """
        import json

        package_json_path = self.working_dir / "package.json"

        if not package_json_path.exists():
            return {}

        try:
            with open(package_json_path, 'r') as f:
                package_json = json.load(f)
                return package_json.get('scripts', {})
        except (json.JSONDecodeError, IOError):
            return {}

    def has_script(self, script_name: str) -> bool:
        """Check if a specific npm script exists.

        Args:
            script_name: Script name (e.g., 'build', 'test')

        Returns:
            True if script exists
        """
        scripts = self.get_package_scripts()
        return script_name in scripts

    def run_npm_script(self, script_name: str, timeout: Optional[int] = None) -> ExecutionResult:
        """Run an npm script.

        Args:
            script_name: Script name from package.json
            timeout: Optional timeout override

        Returns:
            ExecutionResult from script execution
        """
        if not self.has_script(script_name):
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                duration=0.0,
                error=f"Script '{script_name}' not found in package.json",
            )

        return self.run_command(["npm", "run", script_name], timeout=timeout)
