#service_runner.py
import sys
import time
import signal
from utils.logging_utils import setup_logger
from subprocess import Popen
import psutil
from utils.logging_utils import setup_logger, log_function_call

logger = setup_logger('service_runner', 'service_runner.log')

@log_function_call(logger)
class ServiceRunner:
    def __init__(self, script_path: str, service_name: str):
        self.script_path = script_path
        self.service_name = service_name
        self.process = None
        self.should_run = True
        self.logger = setup_logger(f'{service_name}_runner', f'{service_name}_runner.log')

        # Настраиваем обработчики сигналов
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
    
    def handle_signal(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        self.logger.info(f"Received signal {signum}. Stopping {self.service_name}...")
        self.should_run = False
        if self.process:
            self.stop_process()

    def stop_process(self):
        """Корректно останавливает процесс и все дочерние процессы"""
        if self.process:
            try:
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                self.process = None
                self.logger.info(f"{self.service_name} process stopped")
            except psutil.NoSuchProcess:
                pass

    def run(self):
        """Запускает и поддерживает работу сервиса"""
        self.logger.info(f"Starting {self.service_name} service runner")

        while self.should_run:
            try:
                self.logger.info(f"Starting {self.service_name} process")
                self.process = Popen([sys.executable, self.script_path])

                # Ждем завершения процесса
                self.process.wait()

                # Если процесс завершился с ошибкой
                if self.process.returncode != 0 and self.should_run:
                    self.logger.error(
                        f"{self.service_name} process ended with return code "
                        f"{self.process.returncode}. Restarting in 5 seconds..."
                    )
                    time.sleep(5)
                else:
                    self.logger.info(f"{self.service_name} process ended normally")

            except Exception as e:
                self.logger.error(f"Error in {self.service_name} runner: {str(e)}")
                if self.should_run:
                    time.sleep(5)

        self.logger.info(f"{self.service_name} service runner stopped")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python service_runner.py <script_path> <service_name>")
        sys.exit(1)

    script_path = sys.argv[1]
    service_name = sys.argv[2]

    runner = ServiceRunner(script_path, service_name)
    runner.run()