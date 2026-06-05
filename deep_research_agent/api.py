from __future__ import annotations

from fastapi import FastAPI

from deep_research_agent.models import ResearchRequest, ResearchResponse
from deep_research_agent.workflow import ResearchWorkflow

app = FastAPI(title="Deep Research Agent", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/research", response_model=ResearchResponse)
def create_research(request: ResearchRequest) -> ResearchResponse:
    workflow = ResearchWorkflow(
        output_dir=request.output_dir,
        provider=request.provider,
        demo=request.demo,
    )
    result = workflow.run(request.topic)
    return ResearchResponse(
        topic=result.state.topic,
        markdown=result.markdown,
        report_path=str(result.report_path),
        review=result.review,
    )
