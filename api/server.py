from fastapi import FastAPI
from core.intelligence import CoreIntelligence
from memory.experience_memory import ExperienceMemory
from evolution.self_evolver import SelfEvolver

app = FastAPI(
    title="Self-Evolving Intelligence",
    description="An adaptive intelligence system that evolves without retraining",
    version="1.0"
)

core = CoreIntelligence()
memory = ExperienceMemory()
evolver = SelfEvolver(memory)

@app.get("/")
def root():
    return {
        "message": "Self-Evolving Intelligence API is running",
        "status": "active",
        "endpoints": ["/decide", "/docs"]
    }

@app.post("/decide")
def decide(input_signal: list[int]):
    decision, decision_details = core.decide(input_signal, return_details=True)

    reward = 1 if decision == "Action-A" else -1
    memory.store(
        input_signal,
        decision,
        reward,
        metadata={
            "confidence": decision_details["confidence"],
            "strategy_weight": decision_details["strategy_weight"],
            "decision_details": decision_details,
        },
    )
    evolution_update = evolver.evolve(core)

    return {
        "input": input_signal,
        "decision": decision,
        "decision_details": decision_details,
        "evolution_update": evolution_update,
        "strategy_weight": core.strategy_weight,
        "memory_size": len(memory.experiences)
    }
