from enum import Enum

n = 1

# Possible values of a fact
class Value(Enum):
    true = "True"
    false = "False"
    unknown = "Unknown"
    
# Data class to store state of a fact
class Fact():
    
    def __init__(self, text, val=Value.unknown):
        
        self.text = text
        self.propagated = False
        self.value = val
        
    def __repr__(self):
        return self.text + " = " + str(self.value.value)
        
        
# Data class representing 1 single rule
class Rule():
    
    def __init__(self, strRule):
        global n
        
        # Id for each rule
        self.number = n
        n += 1
        
        self.active = False
        self.pre, self.post = [], []
        [strPre,separator,strPost] = strRule.partition("=>")
        if separator == "": # implication not found
          raise Exception("Missing '=>' in rule") 
        self.pre = [s.strip() for s in strPre.split("&")]
        self.post = [s.strip() for s in strPost.split("&")]
        self.active = True
    
    def removeAtom(self, fact):
        assert fact in self.pre
        self.pre.remove(fact)
        
    def isEmpty(self):
        return self.pre == []
        
    def __repr__(self):
        return "Rule n°" + str(self.number) + ": " + str(self.pre) + " => " + str(self.post)

    
# Expert trying to get as much information as possible given rules and facts
class Expert():

    def __init__(self, verb = True):
        self.facts=[]
        self.rules=[]
        self.verb = verb

    def addRule(self,r):
        if self.verb: print(f"Adding rule {r}")
        self.rules.append(r)
        
    def removeRule(self, r):
        if self.verb: print(f"Removing rule {r.number}")
        self.rules.remove(r)

    def addFact(self,f):
        if self.verb: print(f"Adding fact {f.text}")
        self.facts.append(f)

    def rectractFact(self,f):
        if self.verb: print(f"Removing fact {f.text}")
        self.facts.remove(f)

    # Returns the list of rules that contains this fact as a pre
    def _getRulesForFactPre(self, fact):
        return [rule for rule in self.rules if fact.text in rule.pre]
    
    # Returns the list of rules that contains this fact as a post
    def _getRulesForFactPost(self, fact):
        return [rule for rule in self.rules if fact.text in rule.post]

    # Ask the user about the fact f
    def _ask(self, f):
        
        choice = None
        while choice not in [1, 2, 3]:
            choice = int(input("Is " + f.text + " true(1), false(2) or unknown(3): "))
            
        if choice == 1:
            f.value = Value.true
            self.addFact(f)
            return True
        
        elif choice == 2:
            f.value = Value.false
            return False
        
        else:
            f.value = Value.unknown
            return False
           
    # Backward chaining with questions
    def BackwardChaining(self, fact):
        
        already_tried = []
        
        for rule in self._getRulesForFactPost(fact):
            for pre in rule.pre:
                
                # Avoid to loop on some facts
                if pre not in already_tried:
                    already_tried.append(pre)
                    ret = self.BackwardChaining(Fact(pre))
                    
            if ret: return True
        
        return self._ask(fact)
        
    
    # Forward chaining with fact propagation
    def ForwardChaining(self, facts):
        
        #self.facts = facts
        
        for f in facts:
            self.Propagate(f)
            f.propagated = True
            
    
    # Propagates 1 fact through the rules concerned
    def Propagate(self, fact):
        new_facts = []
        
        for rule in self._getRulesForFactPre(fact):
            rule.removeAtom(fact.text)
            
            if rule.isEmpty():
                self.removeRule(rule)
                
                # Disjunction of new_facts and conclusions(r)
                new_facts = list(set(new_facts + [Fact(r, val=Value.true) for r in rule.post]))
        
        # Add new facts to our facts data structure
        self.facts = list(set(self.facts + new_facts))
        
        # Propagate new facts found
        for f in new_facts:
            self.Propagate(f)
            
    
    def Proceed(self, facts):
        
        if self.verb: print(f"Base facts are : {facts}")
        if self.verb: print("Forwarding...")
        
        self.fact = facts
        self.ForwardChaining(facts)
        
        if self.rules:
            for rule in self.rules:
                for p in rule.post:
                    if self.verb: print(f"Backwarding on {p}...")
                    ret = self.BackwardChaining(Fact(p))
                    
                    if ret:
                        self.ForwardChaining([fact for fact in self.facts if not fact.propagated])
                            
        self.Recap()
        
                            
    def Recap(self):
        print(f"Facts: {self.facts}")

        
expert = Expert()

expert.addRule(Rule("promesses-irréalistes => démagogie"))
expert.addRule(Rule("attaques-personnelles => démagogie"))
expert.addRule(Rule("démagogie & casseroles & contrôle-média => gagne-élection"))
expert.addRule(Rule("pas-casseroles & déjà-présenté => gagne-élection"))
expert.addRule(Rule("démagogie & pas-casseroles => gagne-élection"))
expert.addRule(Rule("a-déjà-perdu => déjà-présenté"))
expert.addRule(Rule("patron-chaine => contrôle-média"))
expert.addRule(Rule("mari-patronne => contrôle-média"))

BF = [Fact("attaques-personnelles", val=Value.true), Fact("patron-chaine", val=Value.true), Fact("casseroles", val=Value.true)]
expert.Proceed(BF)