import time
from uuid import uuid4
from brain.retrieval.hybrid_retriever import HybridRetriever
from brain.memory.importance_scorer import MemoryImportanceScorer


from database.user_repository import UserRepository

from brain.chat.chat_engine import ChatEngine
from brain.base.brain_request import BrainRequest

from brain.memory.message_analyzer import MessageAnalyzer
from brain.router.decision_router import DecisionRouter
from brain.engine.engine_registry import EngineRegistry
from brain.memory.memory_engine import MemoryEngine

from brain.memory.sqlalchemy_repository import SQLAlchemyMemoryRepository
from brain.memory.memory_service import MemoryService
from brain.memory.extractor import MemoryExtractor
from brain.memory.resolver import MemoryResolver
from brain.memory.writer import MemoryWriter
from brain.memory.validator import MemoryValidator
from brain.memory.memory_cleaner import MemoryCleaner

from brain.llm.llm_factory import LLMFactory
from brain.llm.memory_llm_service import MemoryLLMService
from brain.llm.usage_tracker import UsageTracker
from brain.llm.deepseek_service import DeepSeekService
from brain.llm.llm_request_context import LLMRequestContext


from decimal import Decimal

from brain.recharge.calculator import (
    BrainUnitCalculator,
    CostBasedBrainUnitPolicy,
)
from brain.recharge.cost.cost_resolver import ExecutionCostResolver
from brain.recharge.cost.passthrough_cost_source import (
    PassthroughExecutionCostSource,
)
from brain.recharge.settlement import BrainUsageSettlementService
from brain.recharge.usage_adapter import LLMUsageToBrainUsageAdapter
from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.wallet.service import BrainWalletService
from brain.recharge.wallet.transaction_repository import (
    BrainTransactionRepository,
)

from brain.recharge.cost.deepseek_cost_source import (
    DeepSeekCostSource,
)
from brain.recharge.wallet.wallet_operations import BrainWalletOperations
from brain.recharge.config import DEV_BRAIN_RECHARGE_CONFIG
from brain.recharge.entitlement.consumption import (
    FreeBrainConsumptionPolicy,
)
from brain.recharge.entitlement.repository import (
    FreeBrainEntitlementRepository,
)
from brain.recharge.entitlement.reset_policy import (
    FreeBrainResetPolicy,
)
from brain.recharge.entitlement.service import (
    FreeBrainEntitlementService,
)
from brain.recharge.settlement_repository import (
    BrainSettlementRepository,
)



from brain.recharge.included_capacity_service import (
    IncludedBrainCapacityService,
)
from brain.tier.capacity.capacity_service import (
    PersistentTierCapacityService,
)
from brain.tier.capacity.repository import (
    TierBrainCapacityRepository,
)

from brain.context.context_model import Context
from brain.context.context_builder import ContextBuilder
from brain.context.context_assembler import ContextAssembler

from brain.conversation.conversation_service import ConversationService
from brain.conversation.conversation_scorer import ConversationScorer
from brain.conversation.conversation_title_generator import ConversationTitleGenerator
from brain.conversation.conversation_summary_service import (
    ConversationSummaryService,
)
from brain.conversation.conversation_summary_orchestrator import (
    ConversationSummaryOrchestrator,
)
from brain.conversation.conversation_summary_generator import (
    ConversationSummaryGenerator,
)
from brain.conversation.conversation_summary_policy import (
    ConversationSummaryPolicy,
)


from brain.tier.capability_resolver import CapabilityResolver
from brain.tier.default_models import create_default_model_registry
from brain.tier.model_router import ModelRouter
from brain.tier.models import BrainTier
from brain.tier.entitlement.service import TierEntitlementService
from brain.tier.entitlement.validator import TierEntitlementValidator
from brain.tier.entitlement.errors import TierEntitlementError

from brain.reasoning.engine import ReasoningEngine


from brain.tools.tool_registry import ToolRegistry
from brain.tools.tool_executor import ToolExecutor
from brain.tools.tool_pipeline import ToolPipeline
from brain.tools.tool_decision_coordinator import ToolDecisionCoordinator
from brain.tools.calculator_tool import CalculatorTool
from brain.tools.tool_call_builder import ToolCallBuilder
from brain.tools.tool_argument_extractor import ToolArgumentExtractor

from brain.language.language_pipeline import LanguagePipeline

#project imports
from brain.project.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from brain.project.sqlalchemy_goal_repository import (
    SQLAlchemyGoalRepository,
)
from brain.project.sqlalchemy_task_repository import (
    SQLAlchemyProjectTaskRepository,
)
from brain.project.project_context_resolver import (
    ProjectContextResolver,
)
from brain.project.project_context_formatter import (
    ProjectContextFormatter,
)
from brain.project.sqlalchemy_decision_repository import (
    SqlAlchemyProjectDecisionRepository,
)

from brain.note.note_retriever import NoteRetriever
from brain.note.sqlalchemy_note_repository import SQLAlchemyNoteRepository
from brain.private_session.private_session_service import (
    private_session_service,
)
from brain.self_development.integration.core_integration_service import (
    CoreIntegrationService,
)
from brain.self_development.integration.core_execution_signal import (
    CoreExecutionSignal,
)
from brain.self_development.observation.signal_detector import (
    SignalDetector,
)
from brain.self_development.improvement.improvement_manager import (
    ImprovementManager,
)
from brain.self_development.observation.observation_coordinator import (
    ObservationCoordinator,
)
from services.guest_session_service import (
    guest_session_service,
)
from brain.llm.usage_persistence import LLMUsagePersistence
from brain.llm.llm_telemetry_signal_evaluator import (
    LLMTelemetrySignalEvaluator,
)
from brain.llm.usage_record_handler import (
    LLMUsageRecordHandler,
)


class BrainOrchestrator:

    """
    Central coordinator of IRABRAIN.

    The orchestrator controls execution order.

    Business logic belongs inside:
    - services
    - engines
    - analyzers
    - pipelines
    - repositories
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, db,
                 core_integration_service: CoreIntegrationService | None = None,):

        print("\n")
        print("=" * 70)
        print("              IRABRAIN ORCHESTRATOR INITIALIZING")
        print("=" * 70)

        # =================================================
        # LLM SERVICES
        # =================================================

        print("\n[1] Initializing LLM services...")
        self.llm_service = MemoryLLMService(
            provider=DeepSeekService(
                model="deepseek-flash"
    )
)

        print("[OK] Base DeepSeek LLM initialized")
        print("[OK] MemoryLLMService initialized")



        print("[OK] UsageTracker initialized")

        # =================================================
        # MESSAGE ANALYSIS
        # =================================================

        print("\n[2] Initializing message analysis...")

        self.message_analyzer = MessageAnalyzer(
            llm_service=self.llm_service
        )

        print("[OK] MessageAnalyzer initialized")

        # =================================================
        # ROUTING / INTENT
        # =================================================

        print("\n[3] Initializing routing and intent...")

        self.router = DecisionRouter()

        self.registry = EngineRegistry()

        self.capability_resolver = CapabilityResolver()
        self.model_registry = create_default_model_registry()
        self.model_router = ModelRouter(self.model_registry)
        self.tier_entitlement_service = TierEntitlementService()
        self.tier_entitlement_validator = TierEntitlementValidator()



        print("[OK] DecisionRouter initialized")
        print("[OK] EngineRegistry initialized")

        # =================================================
        # TOOL SYSTEM
        # =================================================

        print("\n[4] Initializing tool system...")

        self.tool_registry = ToolRegistry()

        self.tool_registry.register(
            CalculatorTool()
        )

        self.tool_decision_coordinator = (
            ToolDecisionCoordinator(
                registry=self.tool_registry,
                llm_service=self.llm_service,

            )
        )

        self.tool_argument_extractor = (
            ToolArgumentExtractor(
                registry=self.tool_registry,
                llm_service=self.llm_service,
            )
        )

        self.tool_call_builder = ToolCallBuilder(
            extractor=self.tool_argument_extractor
        )

        self.tool_executor = ToolExecutor(
            self.tool_registry
        )

        self.tool_pipeline = ToolPipeline(
            registry=self.tool_registry,
            executor=self.tool_executor
        )

        print("[OK] ToolRegistry initialized")
        print("[OK] CalculatorTool registered")
        print("[OK] ToolDecisionCoordinator initialized")
        print("[OK] ToolArgumentExtractor initialized")
        print("[OK] ToolCallBuilder initialized")
        print("[OK] ToolExecutor initialized")
        print("[OK] ToolPipeline initialized")

        # =================================================
        # LANGUAGE
        # =================================================

        print("\n[5] Initializing language pipeline...")

        self.language_pipeline = LanguagePipeline()

        print("[OK] LanguagePipeline initialized")

        # =================================================
        # DATABASE
        # =================================================

        print("\n[6] Initializing database session...")

        self.session = db

        self.user_repository = UserRepository(self.session)

        usage_persistence = LLMUsagePersistence(
            session=self.session
)

        telemetry_evaluator = (
            LLMTelemetrySignalEvaluator()
)

        signal_detector = SignalDetector()

        improvement_manager = ImprovementManager()

        observation_coordinator = ObservationCoordinator(
            signal_detector=signal_detector,
            improvement_manager=improvement_manager,
)

        wallet_repository = BrainWalletRepository(
            self.session
)

        transaction_repository = BrainTransactionRepository(
            self.session
)

        wallet_service = BrainWalletService()

        wallet_operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=wallet_service,
)

        recharge_config = DEV_BRAIN_RECHARGE_CONFIG

        self.cost_resolver = ExecutionCostResolver(
            sources=[

                DeepSeekCostSource(
                    input_cost_per_million=(
                        recharge_config.deepseek.input_cost_per_million
    ),
                    output_cost_per_million=(
                        recharge_config.deepseek.output_cost_per_million
    ),
                    cached_input_cost_per_million=(
                         recharge_config.deepseek.cached_input_cost_per_million
    ),
                    version=recharge_config.deepseek.version,
),
    ]
)

        brain_unit_calculator = BrainUnitCalculator(
            policy=CostBasedBrainUnitPolicy(
                unit_cost=recharge_config.brain_units.unit_cost,
                version=recharge_config.brain_units.version,
                target_currency=recharge_config.brain_units.currency,
                usd_to_inr_rate=recharge_config.brain_units.usd_to_inr_rate,
    )
)

        free_brain_service = FreeBrainEntitlementService(
            repository=FreeBrainEntitlementRepository(
                self.session
    ),
            reset_policy=FreeBrainResetPolicy(),
            consumption_policy=FreeBrainConsumptionPolicy(),
)

        tier_capacity_repository = TierBrainCapacityRepository(
            self.session
)

        tier_capacity_service = PersistentTierCapacityService(
            repository=tier_capacity_repository,
)

        included_capacity_service = IncludedBrainCapacityService(
            free_brain_service=free_brain_service,
            tier_capacity_service=tier_capacity_service,
)




        settlement_repository = BrainSettlementRepository(
            self.session
)

        settlement_service = BrainUsageSettlementService(
            cost_resolver=self.cost_resolver,
            wallet_operations=wallet_operations,
            included_capacity_service=included_capacity_service,
            settlement_repository=settlement_repository,
)

        brain_usage_adapter = LLMUsageToBrainUsageAdapter(
            settlement_service=settlement_service,
            unit_calculator=brain_unit_calculator,
)

        usage_handler = LLMUsageRecordHandler(
            persistence=usage_persistence,
            telemetry_evaluator=telemetry_evaluator,
            observation_coordinator=observation_coordinator,
            brain_usage_adapter=brain_usage_adapter,
)

        self.usage_tracker = UsageTracker(
            record_handler=usage_handler.handle
)
        self.observation_coordinator = observation_coordinator



        self.chat_llm = LLMFactory.create_chat_service(
            usage_tracker=self.usage_tracker,
            provider="deepseek",
            cost_resolver=self.cost_resolver,
)

        self.llm_service = MemoryLLMService(
            provider=self.chat_llm
)
        self.llm_service.provider = self.chat_llm

        print("[OK] UsageTracker initialized")
        print("[OK] LLM usage persistence initialized")
        print("[OK] Chat LLM initialized: deepseek-flash")
        print("[OK] MemoryLLMService initialized")


        self.core_integration_service = (
            core_integration_service
            or CoreIntegrationService()
)



        # =================================================
# NOTES
# =================================================

        note_repository = SQLAlchemyNoteRepository(
            session=self.session
)

        self.note_retriever = NoteRetriever(
            repository=note_repository
)

        print("[OK] NoteRetriever initialized")





                # =================================================
        # PROJECT CONTEXT
        # =================================================

        print("\n[6.1] Initializing project context...")

        self.project_context_resolver = ProjectContextResolver(
            project_repository=SQLAlchemyProjectRepository(
                self.session
            ),
            goal_repository=SQLAlchemyGoalRepository(
                self.session
            ),
            task_repository=SQLAlchemyProjectTaskRepository(
                self.session
            ),
            decision_repository=SqlAlchemyProjectDecisionRepository(
                self.session),
        )

        print("[OK] ProjectContextResolver initialized")

        print("[OK] Database session attached")

        # =================================================
        # CONVERSATION
        # =================================================

        print("\n[7] Initializing conversation system...")

        conversation_scorer = ConversationScorer(
            llm_service=self.llm_service
        )

        self.conversation_service = ConversationService(
            db=self.session,
            scorer=conversation_scorer
        )


        self.conversation_summary_service = (
            ConversationSummaryService(
                db=self.session
    )
)
        self.conversation_summary_generator = (
            ConversationSummaryGenerator(
                llm_service=self.llm_service
    )
)

        self.conversation_summary_policy = (
            ConversationSummaryPolicy()
)

        self.conversation_summary_orchestrator = (
            ConversationSummaryOrchestrator(
                summary_service=self.conversation_summary_service,
                summary_generator=self.conversation_summary_generator,
                policy=self.conversation_summary_policy,
                conversation_repository=self.conversation_service.repository,
    )
)





        self.private_session_service = (
            private_session_service
)
        self.guest_session_service = (
            guest_session_service
)

        self.conversation_title_generator = ConversationTitleGenerator(
            llm_service=self.llm_service
)

        print("[OK] ConversationScorer initialized")
        print("[OK] ConversationService initialized")

        # =================================================
        # REASONING
        # =================================================

        print("\n[8] Initializing reasoning engine...")

        self.reasoning_engine = ReasoningEngine(
            llm_service=self.llm_service
        )

        print("[OK] ReasoningEngine initialized")

        # =================================================
        # MEMORY REPOSITORY
        # =================================================

        print("\n[9] Initializing memory repository...")

        repository = SQLAlchemyMemoryRepository(
            self.session
        )

        self.hybrid_retriever = HybridRetriever(
            repository,
            llm_service=self.llm_service
        )

        print("[OK] SQLAlchemyMemoryRepository initialized")
        print("[OK] HybridRetriever initialized")

        # =================================================
        # MEMORY COMPONENTS
        # =================================================

        print("\n[10] Initializing memory components...")

        resolver = MemoryResolver(
            repository=repository,
            llm_service=self.llm_service
        )

        writer = MemoryWriter(
            repository=repository
        )

        validator = MemoryValidator()

        cleaner = MemoryCleaner()

        memory_extractor = MemoryExtractor(
            llm_service=self.llm_service
        )

        print("[OK] MemoryResolver initialized")
        print("[OK] MemoryWriter initialized")
        print("[OK] MemoryValidator initialized")
        print("[OK] MemoryCleaner initialized")
        print("[OK] MemoryExtractor initialized")

        # =================================================
        # MEMORY SERVICE
        # =================================================

        print("\n[11] Initializing MemoryService...")

        self.memory_service = MemoryService(
            extractor=memory_extractor,
            resolver=resolver,
            writer=writer,
            validator=validator,
            cleaner=cleaner,
            repository=repository,
            importance_scorer=MemoryImportanceScorer()
        )

        print("[OK] MemoryService initialized")

        # =================================================
        # CONTEXT
        # =================================================

        print("\n[12] Initializing context system...")

        self.context_builder = ContextBuilder(
            repository
        )

        self.context_assembler = ContextAssembler(
            context_builder=self.context_builder,
            conversation_service=self.conversation_service,
            conversation_summary_service=(
                self.conversation_summary_service
    )
        )

        print("[OK] ContextBuilder initialized")
        print("[OK] ContextAssembler initialized")

        # =================================================
        # CHAT ENGINE
        # =================================================

        print("\n[13] Initializing ChatEngine...")

        self.chat_engine = ChatEngine(
            llm_service=self.chat_llm
        )

        print("[OK] ChatEngine initialized")

        # =================================================
        # MEMORY ENGINE
        # =================================================

        print("\n[14] Initializing MemoryEngine...")

        memory_engine = MemoryEngine(
            memory_service=self.memory_service
        )

        self.registry.register(
            "memory",
            memory_engine
        )

        print("[OK] MemoryEngine initialized")
        print("[OK] MemoryEngine registered")

        # =================================================
        # COMPLETE
        # =================================================

        print("\n")
        print("=" * 70)
        print("          IRABRAIN ORCHESTRATOR READY")
        print("=" * 70)
        print("\n")

    # =====================================================
    # NORMAL PROCESS
    # =====================================================

    def process(
        self,
        request: BrainRequest
    ) -> str:

        print("\n")
        print("=" * 70)
        print("              BRAIN PROCESS START")
        print("=" * 70)

        print("\n[PROCESS]")
        print("User ID :", request.user_id)
        print("Query   :", request.query)

        start_time = time.perf_counter()

        chunks = []

        try:

            for chunk in self.process_stream(
                request=request
            ):
                chunks.append(chunk)

            response = "".join(chunks)

            execution_time = (
                time.perf_counter() - start_time
        )

            self.core_integration_service.publish(
                CoreExecutionSignal(
                    signal_id=str(uuid4()),
                    operation="brain_process",
                    success=True,
                    execution_time=execution_time,
                     metadata={
                    "workspace_mode": request.metadata.get(
                        "workspace_mode",
                        "personal"
                    )
                },
            )
        )

            print(
            "\n[SELF-DEVELOPMENT SIGNAL] "
            "Core execution signal published"
        )

            print("\n========== BRAIN PROCESS COMPLETE ==========")
            print("Response length :", len(response))
            print("============================================")

            return response

        except Exception as error:

            execution_time = (
                time.perf_counter() - start_time
        )

            self.core_integration_service.publish(
                CoreExecutionSignal(
                    signal_id=str(uuid4()),
                    operation="brain_process",
                    success=False,
                    execution_time=execution_time,
                    error=str(error),
            )
        )

            raise
    # =====================================================
    # STREAMING PROCESS
    # =====================================================

    def process_stream(
        self,
        request: BrainRequest,
        conversation_history=None,
        on_visual=None,
    ):

        print("\n")
        print("=" * 70)
        print("              BRAIN STREAM START")
        print("=" * 70)

        print("\n[REQUEST]")
        print("User ID :", request.user_id)
        print("Query   :", request.query)

       # =================================================
       # 1. SAVE USER MESSAGE
       # =================================================

        print("\n")
        print("========== 1. SAVE USER MESSAGE ==========")

        workspace_mode = request.metadata.get(
            "workspace_mode",
            "personal"
)



        if workspace_mode == "private":

            if not request.session_id:
                raise ValueError(
                    "Private Space requires a session_id"
        )

            self.private_session_service.add_message(
                session_id=request.session_id,
                role="user",
                content=request.query
    )

            user_message = None

            print("[PRIVATE SPACE] User message kept in temporary session")


        elif workspace_mode == "guest":

            if not request.session_id:
                raise ValueError(
                "Guest Space requires a session_id"
        )
            self.guest_session_service.add_message(
                session_id=request.session_id,
                role="user",
                content=request.query
    )
            user_message = None
            print("[GUEST SPACE] User message kept in temporary session")


        else:

            user_message = (
                self.conversation_service.save_user_message(
                    user_id=request.user_id,
                    content=request.query,
                    conversation_id=request.conversation_id,
                    attachments=[
                        {
                            "type": (a.get("type") if isinstance(a, dict) else getattr(a, "type", None)),
                            "name": (a.get("name") if isinstance(a, dict) else getattr(a, "name", None)),
                            "mime_type": (a.get("mime_type") if isinstance(a, dict) else getattr(a, "mime_type", None)),
                            "page_count": (a.get("page_count") if isinstance(a, dict) else getattr(a, "page_count", None)),
                            "status": (a.get("status") if isinstance(a, dict) else getattr(a, "status", None)),
                        }
                        for a in (request.attachments or [])
                        if (a.get("name") if isinstance(a, dict) else getattr(a, "name", None))
                    ]
        )
    )




            print("[OK] User message saved")
            print("Message ID :", user_message.message_id)


        # =================================================
        # 2. MESSAGE ANALYSIS
        # =================================================

        semantic_result = self.message_analyzer.analyze(
            request=request,
            conversation_history=conversation_history,
)

        analysis = self.message_analyzer.to_message_analysis_result(
            semantic_result
)

        intent = self.message_analyzer.to_intent_result(
            semantic_result
)

        print("Intent and message analyzer:", intent)
        print("========================================")

        # =================================================
        # 4. MEMORY RETRIEVAL
        # =================================================

        print("\n")
        print("========== 4. MEMORY RETRIEVAL ==========")

        workspace_mode = request.metadata.get(
            "workspace_mode",
            "personal"
)

        if workspace_mode in ("private", "guest"):

            print(f"[{workspace_mode.upper()} SPACE] Memory retrieval skipped")

            memories = []

        else:

            memories = self.hybrid_retriever.retrieve(
                user_id=request.user_id,
                query=request.query
    )

         # =================================================
            # 4.1 NOTES RETRIEVAL
        # =================================================

        print("\n")
        print("========== 4.1 NOTES RETRIEVAL ==========")

        if workspace_mode in ("private", "guest"):

            notes = []

            print(f"[{workspace_mode.upper()} SPACE] Notes retrieval skipped")


        else:

            notes = self.note_retriever.retrieve(
                user_id=request.user_id,
                query=request.query,
                limit=5
    )

            print("[OK] Notes retrieval complete")
            print("Note count :", len(notes))

        print("==========================================")

        print("[OK] Memory retrieval complete")
        print("Memory count :", len(memories))

        print("=========================================")

        # =================================================
        # 5. TOOL DECISION
        # =================================================

        print("\n")
        print("========== 5. TOOL DECISION ==========")

        tool_decision = (
            self.tool_decision_coordinator.decide(
                request=request,
                intent_result=intent
            )
        )

        print("Tool Decision :", tool_decision)
        print("======================================")

        # =================================================
        # 6. BUILD TOOL CALL
        # =================================================

        print("\n")
        print("========== 6. TOOL CALL ==========")

        tool_call = None

        if tool_decision.requires_tool:

            print("[INFO] Tool required")

            tool_call = self.tool_call_builder.build(
                request=request,
                decision=tool_decision
            )

            print("Tool Call :", tool_call)

        else:

            print("[INFO] No tool required")

        print("==================================")

        # =================================================
        # 7. EXECUTE TOOL
        # =================================================

        print("\n")
        print("========== 7. TOOL EXECUTION ==========")

        tool_result = None

        if tool_call is not None:

            print("[INFO] Executing tool...")

            tool_result = self.tool_pipeline.execute(
                decision=tool_decision,
                call=tool_call
            )

            print("Tool Result :", tool_result)

        else:

            print("[INFO] Tool execution skipped")

        print("=======================================")

        # =================================================
        # 8. LANGUAGE
        # =================================================

        print("\n")
        print("========== 8. LANGUAGE PIPELINE ==========")

        (
            language_result,
            language_policy,
            language_request
        ) = self.language_pipeline.prepare(
            text=request.query,
            analysis=analysis
        )

        print("Detection :", language_result)
        print("Policy    :", language_policy)
        print("Processed :", language_request)

        print("==========================================")

        # =================================================
        # 9. ROUTING
        # =================================================

        print("\n")
        print("========== 9. BRAIN ROUTING ==========")

        routes = self.router.route(
            analysis=analysis,
            intent=intent,
            tool_decision=tool_decision
        )

        print("Routes :", routes)

        print("=======================================")



                # =================================================
        # 9.1 MODEL ROUTING
        # =================================================

        print("\n")
        print("========== 9.1 MODEL ROUTING ==========")

        capability_requirement = (
            self.capability_resolver.resolve(
                analysis=analysis,
                intent=intent,
            )
        )

        workspace_mode = request.metadata.get(
            "workspace_mode",
            "personal",
)

        if workspace_mode == "guest":
            brain_tier = BrainTier.FREE
        else:
            brain_tier_value = self.user_repository.get_brain_tier(
                request.user_id
    )

            brain_tier = BrainTier(brain_tier_value)

        entitlement = self.tier_entitlement_service.get_entitlement(
            brain_tier
)

        print(
       "[ENTITLEMENT DIAGNOSTIC]",
    "tier=", entitlement.tier,
    "capability=", capability_requirement.capability,
    "allowed=", capability_requirement.capability
        in entitlement.allowed_capabilities,
    "required_complexity=", capability_requirement.complexity,
    "max_complexity=", entitlement.max_complexity,
    "required_context=", capability_requirement.required_context_window,
    "max_context=", entitlement.max_context_window,
)

        try:
            self.tier_entitlement_validator.validate(
                entitlement=entitlement,
                requirement=capability_requirement,
    )

        except TierEntitlementError as error:
            if workspace_mode == "personal":
                error_message = (
                  "This task requires a capability that isn't included "
                    "in your current Brain tier."
                    if error.code == "CAPABILITY_NOT_INCLUDED"
                    else
                    "This task requires more reasoning capability than "
                    "your current Brain tier supports."
                    if error.code == "COMPLEXITY_LIMIT_EXCEEDED"
                    else
                    "This task exceeds the context capacity of your "
                    "current Brain tier."
                    if error.code == "CONTEXT_LIMIT_EXCEEDED"
                    else
                    "This task cannot be completed with your current Brain tier."
        )

                self.conversation_service.save_assistant_message(
                    user_id=request.user_id,
                    content=error_message,
                    conversation_id=request.conversation_id,
        )

                self.conversation_service.commit()

            raise

        selected_model = self.model_router.route(
            tier=brain_tier,
            requirement=capability_requirement,
        )

        selected_chat_llm = LLMFactory.create_chat_service(
            usage_tracker=self.usage_tracker,
            provider=selected_model.provider,
            model=selected_model.model_id,
            cost_resolver=self.cost_resolver,
)


        selected_chat_engine = ChatEngine(
            llm_service=selected_chat_llm
)



        print("Capability :", capability_requirement)
        print("Brain Tier :", brain_tier)
        print("Model      :", selected_model.model_id)
        print("Provider   :", selected_model.provider)

        print("========================================")




        # =================================================
        # 10. MEMORY ENGINE
        # =================================================

        print("\n")
        print("========== 10. MEMORY ENGINE ==========")



        if (
            "memory" in routes
            and workspace_mode == "personal"
):

            print("[INFO] Memory route detected")

            memory_engine = self.registry.get(
                "memory"
    )

            print("Memory Engine :", memory_engine)

            if memory_engine:

                print("[INFO] Executing MemoryEngine...")

                memory_engine.execute(
                    request
        )

                print("[OK] MemoryEngine finished")

            else:

                print("[WARNING] MemoryEngine not found")

        elif workspace_mode in ("private", "guest"):

            print(
                 f"[{workspace_mode.upper()} SPACE] Memory pipeline skipped"
    )

        else:

            print("[INFO] Memory route not selected")

        print("=======================================")

        # =================================================
        # 11. CORE IDENTITY
        # =================================================

        print("\n")
        print("========== 11. CORE IDENTITY ==========")

        workspace_mode = request.metadata.get(
            "workspace_mode",
            "personal"
)

        if workspace_mode in ("private", "guest"):

            print(f"[{workspace_mode.upper()} SPACE] Core identity skipped")

            core_identity = {}

        else:

            core_identity = (
                self.memory_service
                .get_core_identity(
                    request.user_id
        )
    )

        print("Core Identity :")
        print(core_identity)

        print("========================================")
        print("SUMMARY_TEST_001")
        # =================================================
        # 12. BUILD CONTEXT
        # =================================================

        print("\n")
        print("========== 12. CONTEXT ASSEMBLY ==========")

        if workspace_mode in ("private", "guest"):

            if workspace_mode == "private":
                temporary_messages = (
                    self.private_session_service
                    .get_messages(request.session_id)
        )
            else:
                temporary_messages = (
                    self.guest_session_service
                    .get_messages(request.session_id)
        )
            assembled_context = Context(
                memory={},
                conversation=temporary_messages
    )



            print(
                f"[{workspace_mode.upper()} SPACE] "
                "Temporary conversation context assembled"
    )

        else:

            assembled_context = (
                self.context_assembler.build(
                    user_id=request.user_id,
                    user_message=request.query,
                    memories=memories,
                    conversation_limit=10,
                    include_memory=bool(memories),
                    current_message_id=user_message.message_id,
                    conversation_id=request.conversation_id
        )
    )


        print("[OK] Context assembled")
        print("ðŸ”¥ðŸ”¥ðŸ”¥ SUMMARY RUNTIME MARKER 999 ðŸ”¥ðŸ”¥ðŸ”¥")
        print(
            "[SUMMARY CHECK]",
            bool(assembled_context.conversation_summary),
            "summary_length=",
            len(assembled_context.conversation_summary or ""),
)

        # =================================================
        # 13. CONVERSATION CONTEXT
        # =================================================

        assembled_conversation = (
            assembled_context.conversation
        )

        print("\n")
        print("========== 13. CONVERSATION CONTEXT ==========")

        print(
            "Conversation messages :",
            len(assembled_conversation)
        )

        for message in assembled_conversation:

            print(
                message.role,
                ":",
                message.content
            )

        print("===============================================")

                # =================================================
        # PROJECT CONTEXT
        # =================================================

        project_context = None

        if request.project_id and workspace_mode not in ("private", "guest"):
            project_context = self.project_context_resolver.resolve(
                project_id=request.project_id,
                user_id=request.user_id,
            )
        project_context_text = None

        if project_context:
            project_context_text = ProjectContextFormatter.format(
                project_context
            )

        # =================================================
        # 14. MEMORY CONTEXT
        # =================================================

        memory_context = (
            assembled_context.memory
            if bool(memories)
            else {}
        )

        # Core identity is always available.
        workspace_mode = request.metadata.get(
            "workspace_mode",
            "personal"
)
        if workspace_mode in ("private", "guest"):
             memory_context = {}

        else:

            memory_context = {
                **core_identity,
                **memory_context
}
        if notes:

            memory_context["notes"] = [
        {
                    "title": note.title,
                    "content": note.content
        }
                for note in notes
    ]

        if workspace_mode == "personal":

            user_name = request.metadata.get(
                "user_name"
    )

            if user_name:
                memory_context["user_profile"] = {
                    "full_name": user_name
        }


        if project_context_text:
            memory_context["project_context"] = project_context_text

        print("\n")
        print("========== 14. MEMORY CONTEXT ==========")

        print(memory_context)

        print("=========================================")

        # =================================================
        # 15. UNIFIED REASONING CONTEXT
        # =================================================

        print("\n")
        print("========== 15. REASONING CONTEXT ==========")

        reasoning_context = Context(
            memory=memory_context,
            conversation=assembled_conversation
        )

        print("[OK] Unified reasoning context created")

        print("===========================================")

        # =================================================
        # 16. MEMORY STATS
        # =================================================

        print("\n")
        print("========== 16. MEMORY STATS ==========")

        workspace_mode = request.metadata.get(
            "workspace_mode",
            "personal"
)

        if (
            analysis.should_enter_memory_pipeline
            and workspace_mode == "personal"


):


            stats = (
                self.memory_service
                .get_stats(
                    request.user_id
                )
            )

            for category, count in stats.items():

                if category == "total":

                    print(
                        f"Total       : {count}"
                    )

                else:
                    print(
                        "[INFO] Memory stats skipped"
    )


                    print(
                        f"{category.capitalize():12} : {count}"
                    )

        else:
            if workspace_mode == "guest":
                print(
                    "[GUEST SPACE] Memory stats skipped"
        )
            else:

                print(
                    "[INFO] Memory pipeline not required"
            )

        print("======================================")

        # =================================================
        # 17. REASONING ENGINE
        # =================================================

        print("\n")
        print("========== 17. REASONING ENGINE ==========")

        reasoning_result = None

        if intent.requires_reasoning:

            print("[INFO] Reasoning required")

            reasoning_result = (
                self.reasoning_engine.reason(
                    request=request,
                    context=reasoning_context,
                    language_policy=language_policy
                )
            )

            print("\nReasoning Strategy   :")
            print(reasoning_result.strategy)

            print("\nReasoning Conclusion :")
            print(reasoning_result.conclusion)

            print("\nReasoning Confidence :")
            print(reasoning_result.confidence)

        else:

            print(
                "[INFO] Reasoning not required"
            )

        print("==========================================")

        # =================================================
        # 18. CHAT ENGINE
        # =================================================

        print("\n")
        print("========== 18. CHAT ENGINE ==========")

        full_response = ""

        print("[INFO] Starting ChatEngine stream...")

        for chunk in selected_chat_engine.execute_stream(
            request=request,
            context=memory_context,
            conversation_history=assembled_conversation,
            reasoning_result=reasoning_result,
            tool_result=tool_result,
            language_policy=language_policy,
            brain_tier=brain_tier,
        ):

            full_response += chunk

            yield chunk

        print("\n[OK] ChatEngine stream completed")

        print("Response length :")
        print(len(full_response))

        print("====================================")

        # =================================================
        visual_payload = None

        # VISUAL INTELLIGENCE
        # =================================================
        print(
           "[VISUAL DEBUG]",
            "on_visual_is_none =", on_visual is None,
             "response_is_empty =", not bool(full_response.strip()),
)
        if on_visual is not None and full_response.strip():
            try:
                print("\n[VISUAL INTELLIGENCE] Generating visual...")
                request_context = LLMRequestContext(
                    request_id=request.request_id,
                    user_id=request.user_id,
                    brain_tier=brain_tier,
                )
                visual_payload = selected_chat_engine.generate_visual(
                    user_message=request.query,
                    assistant_response=full_response,
                    request_context=request_context,
                )

                if visual_payload is not None:
                    on_visual(visual_payload)
                    print("[VISUAL INTELLIGENCE] Visual generated.")
                else:
                    print("[VISUAL INTELLIGENCE] No visual needed.")

            except Exception as error:
                print(
                    "[VISUAL INTELLIGENCE] Integration failed:",
                    str(error),
                )

        # =================================================

        # 19. SAVE ASSISTANT RESPONSE
        # =================================================

        print("\n")
        print("========== 19. SAVE ASSISTANT RESPONSE ==========")

        if workspace_mode == "private":

            self.private_session_service.add_message(
                session_id=request.session_id,
                role="assistant",
                content=full_response
    )

            print(
                  "[PRIVATE SPACE] Assistant response kept in temporary session"
    )
        elif workspace_mode == "guest":

            self.guest_session_service.add_message(
                session_id=request.session_id,
                role="assistant",
                content=full_response
    )

            print(
                "[GUEST SPACE] Assistant response kept in temporary session"
    )

        else:

            self.conversation_service.save_assistant_message(
                user_id=request.user_id,
                content=full_response,
                conversation_id=request.conversation_id,
                visual_data=visual_payload
    )

            print("[OK] Assistant response saved")

            if request.conversation_id:
                summary_result = (
                   self.conversation_summary_orchestrator.summarize_if_needed(
                       conversation_id=request.conversation_id,
                       user_id=request.user_id,
        )
    )

                if summary_result is not None:
                    self.conversation_service.commit()



        print("===================================================")




        print("===================================================")

        # =================================================
        # COMPLETE
        # =================================================

        print("\n")
        print("=" * 70)
        print("              BRAIN STREAM COMPLETE")
        print("=" * 70)
        print("\n")

    # =====================================================
    # GET CONVERSATION
    # =====================================================

    def get_conversation(
        self,
        user_id: int
    ):

        print("\n")
        print("========== GET CONVERSATION ==========")

        print("User ID :", user_id)

        messages = (
            self.conversation_service
            .get_recent_conversation(
                user_id=user_id,
                limit=50
            )
        )

        print(
            "Messages retrieved :",
            len(messages)
        )

        result = [
            {
                "id": message.message_id,
                "role": message.role,
                "content": message.content
            }
            for message in messages
        ]

        print("======================================")

        return result

    # =====================================================
    # CLEANUP
    # =====================================================

    def close(self):

        print("\n========== BRAIN ORCHESTRATOR CLOSE ==========")

        if self.session:

            self.session.close()

            print("[OK] Database session closed")

        print("===============================================")
