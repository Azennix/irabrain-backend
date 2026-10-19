from abc import ABC, abstractmethod
import time

from brain.base.brain_response import BrainResponse
from brain.base.brain_request import BrainRequest


class BaseEngine(ABC):
    """
    Base class for all IRABRAIN engines.
    """

    def process(self, request: BrainRequest) -> BrainResponse:

        start_time = time.perf_counter()

        try:
            result = self.execute(request)

            execution_time = time.perf_counter() - start_time

            return BrainResponse(
                success=True,
                data=result,
                execution_time=execution_time
            )

        except Exception as e:

            execution_time = time.perf_counter() - start_time

            return BrainResponse(
                success=False,
                metadata={
                    "error": str(e)
                },
                execution_time=execution_time
            )

    @abstractmethod
    def execute(self, request: BrainRequest):
        """
        Every engine must implement this method.
        """
        pass