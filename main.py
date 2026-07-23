from core.intelligence import CoreIntelligence
from memory.experience_memory import ExperienceMemory
from evolution.self_evolver import SelfEvolver

core = CoreIntelligence()
memory = ExperienceMemory()
evolver = SelfEvolver(memory)

inputs = [
    [1, -1, 2],
    [-2, -1, -3],
    [3, 1, 1]
]

for inp in inputs:
    decision = core.decide(inp)
    reward = 1 if decision == "Action-A" else -1

    memory.store(inp, decision, reward)
    evolver.evolve(core)

    print(f"Input: {inp}, Decision: {decision}, Strategy Weight: {core.strategy_weight}")
    