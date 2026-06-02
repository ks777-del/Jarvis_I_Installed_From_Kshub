from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .core import (
    BuildValidator,
    CodeGeneratorEngine,
    CompilerEngine,
    ContextEngine,
    DebuggerEngine,
    DependencyManager,
    MemoryMapper,
    MultiFileEditor,
    PatchEngine,
    ProjectAnalyzer,
    ProjectManager,
    ReasoningEngine,
    RefactorEngine,
    SafeExecutionEngine,
    SandboxEngine,
    SecurityValidator,
    TestRunner,
    UIEventStream,
)


@dataclass
class CodeEngineRequest:
    prompt: str
    auto_build: bool = False
    runtime_command: Optional[List[str]] = None


class JarvisCodeEngine:
    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.module_root = Path(__file__).resolve().parent

        self.templates_dir = self.module_root / "templates"
        self.models_dir = self.module_root / "models"
        self.sandbox_dir = self.module_root / "sandbox"
        self.cache_dir = self.module_root / "cache"
        self.logs_dir = self.module_root / "logs"
        self.builds_dir = self.module_root / "builds"
        self.executables_dir = self.module_root / "executables"
        self.backups_dir = self.module_root / "backups"

        for d in [self.sandbox_dir, self.cache_dir, self.logs_dir, self.builds_dir, self.executables_dir, self.backups_dir, self.models_dir, self.templates_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.execution = SafeExecutionEngine(self.workspace, self.logs_dir)
        self.security = SecurityValidator()
        self.sandbox = SandboxEngine(self.sandbox_dir)
        self.analyzer = ProjectAnalyzer(self.workspace)
        self.context = ContextEngine(self.workspace)
        self.memory = MemoryMapper(self.cache_dir)
        self.reasoning = ReasoningEngine(self.workspace)
        self.generator = CodeGeneratorEngine(self.workspace, self.templates_dir, self.models_dir)
        self.editor = MultiFileEditor(self.workspace, self.backups_dir)
        self.patcher = PatchEngine(self.workspace)
        self.debugger = DebuggerEngine(self.workspace, self.execution)
        self.compiler = CompilerEngine(self.workspace, self.execution)
        self.dependencies = DependencyManager(self.workspace, self.execution)
        self.refactor = RefactorEngine(self.workspace)
        self.tests = TestRunner(self.workspace, self.execution)
        self.build_validator = BuildValidator(self.workspace, self.execution)
        self.projects = ProjectManager(self.workspace, self.cache_dir)

    def execute(self, request: CodeEngineRequest, ui_callback: Optional[Callable[[Dict[str, object]], None]] = None) -> Dict[str, object]:
        prompt = str(request.prompt or "").strip()
        if not prompt:
            return {"status": "error", "message": "Prompt is required."}

        ui = UIEventStream(ui_callback)
        ui.emit("analyzing", "Analyzing request...", 10)
        analysis = self.analyzer.analyze().to_dict()

        ui.emit("planning", "Planning architecture...", 24)
        reasoning = self.reasoning.reason(prompt).to_dict()
        context = self.context.index()

        ui.emit("generating", "Generating systems...", 42)
        artifacts = self.generator.generate_from_request(prompt)
        written_files = self.generator.write_artifacts(artifacts)

        ui.emit("dependencies", "Installing dependencies...", 60)
        dep_summary = {
            "python_missing": self.dependencies.detect_missing_python_modules(["json", "pathlib"]),
            "node": self.dependencies.node_dependencies(),
            "compiler_support": self.dependencies.compiler_support(),
        }

        ui.emit("compiling", "Compiling project...", 78)
        build_result = None
        if request.auto_build:
            entries = analysis.get("entry_points") or []
            entry = entries[0] if entries else "main.py"
            if str(entry).endswith(".py"):
                build_result = self.compiler.compile_python(entry, name="jarvis_generated").to_dict()

        ui.emit("validating", "Running validation...", 90)
        syntax = self.tests.syntax_test()
        runtime = self.tests.runtime_test(request.runtime_command, timeout_sec=120) if request.runtime_command else None
        static_issues = [i.to_dict() for i in self.debugger.scan_static()]

        status = "success"
        if syntax.get("status") != "success":
            status = "error"
        if runtime and runtime.get("status") != "success":
            status = "error"

        self.memory.set("last_run", {
            "prompt": prompt,
            "status": status,
            "written_files": written_files,
            "syntax": syntax,
        })

        ui.emit("complete", "Build Complete", 100)

        return {
            "status": status,
            "analysis": analysis,
            "context": context,
            "reasoning": reasoning,
            "written_files": written_files,
            "dependencies": dep_summary,
            "build_result": build_result,
            "syntax_validation": syntax,
            "runtime_validation": runtime,
            "static_issues": static_issues,
            "events": [e.to_dict() for e in ui.events],
        }

    def create_project(self, prompt: str) -> Dict[str, object]:
        return self.execute(CodeEngineRequest(prompt=prompt))

    def run_command(self, command: List[str], timeout_sec: int = 120) -> Dict[str, object]:
        result = self.execution.run(command, timeout_sec=timeout_sec)
        return result.to_dict()

    def auto_debug(self, command: List[str]) -> Dict[str, object]:
        return self.debugger.debug(command)
