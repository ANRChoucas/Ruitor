class HypothesisSet:
    def __init__(self, knowledge, partial_knowledge, ignorance, conflict=0):

        if not sum([knowledge, partial_knowledge, ignorance, conflict]) == 1:
            print(knowledge, partial_knowledge, ignorance, conflict)
            raise ValueError("The sum of values must be 1")

        self.knowledge = knowledge
        self.partial_knowledge = partial_knowledge
        self.ignorance = ignorance
        self.conflict = conflict

    def __or__(self, other):

        conflict_mass = (
            self.knowledge * other.partial_knowledge
            + self.partial_knowledge * other.knowledge
        )
        ignorance_mass = self.ignorance * other.ignorance
        partial_knowledge_mass = (
            self.partial_knowledge * other.partial_knowledge
            + self.ignorance * other.partial_knowledge
            + self.partial_knowledge * other.ignorance
        )
        knowledge_mass = (
            self.knowledge * other.knowledge
            + self.knowledge * other.ignorance
            + self.ignorance * other.knowledge
        )

        return HypothesisSet(
            knowledge_mass, partial_knowledge_mass, ignorance_mass, conflict_mass
        )

    def __str__(self):
        print(self.knowledge, self.partial_knowledge, self.ignorance, self.conflict)
