# logic_engine.py

#IT24610328---Lab07---Part1---Adding the KnowledgeBase class to store facts (current percepts) and rules (Horn Clauses).
class KnowledgeBase:

    #IT24610328---Lab07---Part1---Attributes

    def __init__(self):
        #IT24610328---Lab07---Part1---Creating a set to store unique string facts (e.g. "TargetVisible").
        self.facts = set()
        #IT24610328---Lab07---Part1---Creating a list to store rules as tuples: ([list_of_premises], "conclusion_string").
        self.rules = []

    #IT24610328---Lab07---Part1---Methods

    #IT24610328---Lab07---Part1---Adding the tell_fact method to add a fact to the facts set.
    def tell_fact(self, fact_string):
        self.facts.add(fact_string)

    #IT24610328---Lab07---Part1---Adding the tell_rule method to append a (premises, conclusion) tuple to the rules list.
    def tell_rule(self, premise_list, conclusion_string):
        self.rules.append((premise_list, conclusion_string))

    #IT24610328---Lab07---Part1---Adding the clear_facts method to empty the facts set.
    def clear_facts(self):
        self.facts.clear()

    #IT24610328---Lab07---Part2---Adding the forward_chain method implementing data-driven forward chaining.
    def forward_chain(self):
        new_facts_added = True

        #IT24610328---Lab07---Part2---Iterating over the rules until a full pass deduces no new facts.
        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:
                if conclusion not in self.facts:

                    #IT24610328---Lab07---Part2---Checking Modus Ponens, if all premises are in facts, adding the conclusion.
                    if all(premise in self.facts for premise in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True