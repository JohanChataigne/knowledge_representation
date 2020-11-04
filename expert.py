class Rule():
    
    def __init__(self, strRule):
        self.active = False
        self.pre, self.post = [], []
        [strPre,separator,strPost] = strRule.partition("=>")
        if separator == "": # implication not found
          raise Exception("Missing '=>' in rule") 
        self.pre = [s.strip() for s in strPre.split("&")]
        self.post = [s.strip() for s in strPost.split("&")]
        self.active = True
        
    def __str__(self):
        return str(self.pre) + " => " + str(self.post)



class KB():

    def __init__(self, verb = True):
        self.facts=[]
        self.rules=[]
        self.verb = verb

    def addRule(self,r):
        self.rules.append(r)

    def addFact(self,f):
        print("Adding fact ", f)
        self.facts.append(f)

    def rectractFact(self,f):
        self.facts.remove(f)

    def _propagateRule(self,rule):
        empty = True
        ret = False
        for pre in rule.pre:
            if self.verb: print("evaluating ", pre)
            if pre not in self.facts:
                empty = False
                break
        if empty:
            if self.verb: print("Propagating rule " + str(rule.pre) + " => " + str(rule.post))
            for post in rule.post:
                if post not in self.facts:
                    if self.verb: print("Adding " + post + " as a new fact") 
                    self.addFact(post)
                    ret = True # At least one fact has been added
            rule.active = False
        return ret

    def simpleFC(self):
        "Simple Forward Checking algorithm. No smart data structure used"
        loop = True # True if any fact has been added
        while loop:
            loop = False
            for rule in self.rules:
                if rule.active:
                    loop |= self._propagateRule(rule)

    def _getRulesForFact(self, fact):
        "Returns the list of rules that contains this fact as a post"
        return [rule for rule in self.rules if fact in rule.post]

    def _ask(self, f):
        
        choice = None
        while choice not in [1, 2, 3]:
            choice = int(input("Is " + str(f) + " true(1), false(2) or unknown(3): "))
            
        if choice == 1:
            print("Fact " + str(f) + " added !")
            self.addFact(f)
        else:
            print("Fact " + str(f) + " not added !")
            
        return
        

    def simpleBC(self, fact):
        "Simple Backward chaining for a fact, returns after any new fact is added after any question"
        print("BC for fact " + str(fact))
        for rule in self._getRulesForFact(fact):
            print(rule)
            for pre in rule.pre:
                if pre not in self.facts:
                    rulespre = self._getRulesForFact(pre)
                    if not rulespre: # no rules conclude on it. This is an askable fact
                        self._ask(pre)
                return self.simpleBC(pre)
            
    def trueBC(self, fact):
        if fact in self.facts:
            return True
        
        for rule in self._getRulesForFact(fact):
            



kb = KB()
kb.addRule(Rule("promesses-irréalistes => démagogie"))
kb.addRule(Rule("attaques-personnelles => démagogie"))
kb.addRule(Rule("démagogie & casseroles & contrôle-média => gagne-élection"))
kb.addRule(Rule("pas-casseroles & déjà-présenté => gagne-élection"))
kb.addRule(Rule("démagogie & pas-casseroles => gagne-élection"))
kb.addRule(Rule("a-déjà-perdu => déjà-présenté"))
kb.addRule(Rule("patron-chaine => contrôle-média"))
kb.addRule(Rule("mari-patronne => contrôle-média"))
#kb.simpleFC()
kb.simpleBC("gagne-élection")
kb.simpleFC()
