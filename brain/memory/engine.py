from brain.base.brain_request import BrainRequest

from brain.memory.extractor import MemoryExtractor
from brain.memory.resolver import MemoryResolver
from brain.memory.writer import MemoryWriter
from brain.memory.retriever import MemoryRetriever
from brain.memory.ranker import MemoryRanker
from brain.memory.memory_action import MemoryAction
from brain.memory.memory_result import MemoryResult


class MemoryEngine:

    def __init__(

        self,

        extractor: MemoryExtractor,

        resolver: MemoryResolver,

        writer: MemoryWriter,

        retriever: MemoryRetriever,

        ranker: MemoryRanker

    ):

        self.extractor = extractor

        self.resolver = resolver

        self.writer = writer

        self.retriever = retriever

        self.ranker = ranker


    def process(
    self,
    request: BrainRequest,
     ):

     action = self._determine_action(request)

     if action == MemoryAction.STORE:
        return self._store_memory(request)

     if action == MemoryAction.RETRIEVE:
        return self._retrieve_memory(request)

     return None


    def _store_memory(
    self,
    request: BrainRequest,
):

     extraction_result = self.extractor.extract(request)

     resolution_plan = self.resolver.resolve(
        extraction_result
    )

     writer_result = self.writer.write(
        resolution_plan
    )

     return MemoryResult(
    action=MemoryAction.STORE,
    success=True,
    stored=writer_result.get("inserted", []),
    updated=writer_result.get("updated", [])
)



    def _retrieve_memory(
    self,
    request: BrainRequest,
     ):
       candidate_memories = self.retriever.retrieve(
    request
    )

       ranked_memories = self.ranker.rank(
       request,
      candidate_memories
    )
       return MemoryResult(
    action=MemoryAction.RETRIEVE,
    success=True,
    retrieved=ranked_memories
)