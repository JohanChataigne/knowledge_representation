from enum import Enum

n = 1

# Possible values of a fact
class Value(Enum):
    true = "True"
    false = "False"
    unknown = "Unknown"
    
# Data class to store state of a fact
class Fact():
    
    def __init__(self, text, val=Value.unknown, req=True):
        
        self.text = text
        self.propagated = False
        self.value = val
    
    def hasSameText(self, text):
        return self.text == text
    
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

    
# Expert trying to advise you in your creation of a classification model
class Expert():

    def __init__(self, verb = True, req={}, recaps={}):
        self.requestable_facts = req
        self.recaps = recaps
        self.informational = ['binary', 'multiclass', 'nn', 'ml']
        self.advisable = ['mlp-softmax', 'mlp-sigmoid', 'softmax-regression', 'logistic-regression']

        self.facts=[]
        self.rules=[]
        self._facts=[]
        self._rules=[]
        
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
        
    def Requestable(self, fact):
        return fact.text in self.requestable_facts.keys()

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
            question_text = self.requestable_facts[f.text]
            choice = int(input(question_text + " true(1), false(2) or unknown(3): "))
         
        del self.requestable_facts[f.text]
        
        if choice == 1:
            f.value = Value.true
            self.addFact(f)
            return True
        
        elif choice == 2:
            f.value = Value.false
            self.addFact(f)
            return False
        
        else:
            f.value = Value.unknown
            self.addFact(f)
            return False
           
    # Backward chaining with questions
    def BackwardChaining(self, fact):
        
        if self.verb: print(f"Backwarding on {fact.text}...")
        
        already_tried = []
        
        for rule in self._getRulesForFactPost(fact):
            for pre in rule.pre:
                # Avoid to loop on some facts
                if pre not in already_tried:
                    already_tried.append(pre)
                    ret = self.BackwardChaining(Fact(pre))
                    
            if ret: return True
        
        if self.Requestable(fact):
            return self._ask(fact)
        
        return False
        
    
    # Forward chaining with fact propagation
    def ForwardChaining(self, facts):
        
        if self.verb: print(f"Forwarding on {facts}")
        
        for f in facts:
            self.Propagate(f)
            f.propagated = True
            
            
    
    # Propagates 1 fact through the rules concerned
    def Propagate(self, fact):
        
        if fact.propagated: return
        
        if self.verb: print(f"Propagating on {fact}")

        new_facts = []
        
        for rule in self._getRulesForFactPre(fact):
            
            if fact.value == Value.false:
                
                self.removeRule(rule)
                new_facts = list(set(new_facts + [Fact(r, val=Value.false) for r in rule.post]))
                    
            elif fact.value == Value.true:
                rule.removeAtom(fact.text)
            
                if rule.isEmpty():
                    self.removeRule(rule)
                
                    # Disjunction of new_facts and conclusions(r)
                    new_facts = list(set(new_facts + [Fact(r, val=Value.true) for r in rule.post]))
            
            else:
                new_facts = list(set(new_facts + [Fact(r, val=Value.unknown) for r in rule.post]))
        
        # Add new facts to our facts data structure
        self.facts = list(set(self.facts + new_facts))
        
        
        # Propagate new facts found
        for f in new_facts:
            self.Propagate(f)
            f.propagated = True
            
    
    def Proceed(self, facts=[]):
        
        if self.verb: print(f"Base facts are : {facts}")
        
        self.facts = facts
        self.ForwardChaining(facts)
        
        while self.rules:
            for rule in self.rules:
                for p in rule.post:
                            
                    if not any([f.hasSameText(p) for f in self.facts]):
                        ret = self.BackwardChaining(Fact(p))
                        self.ForwardChaining([fact for fact in self.facts if not fact.propagated])
                            
        self.Recap()
        
                            
    def Recap(self):
        info = ""
        adv = ""
        for f in self.facts:
            if f.text in self.recaps.keys() and f.value == Value.true:
                
                if f.text in self.informational:
                    info += self.recaps[f.text] + '\n'
                else:
                    adv += self.recaps[f.text] + '\n'
        
        ret = "You said that:\n" + info + "From these informations:\n" + adv
        
        if ret == "" or info == "" or adv == "":
            ret = "I can't advise you anything with the information you gave to me :("
                
                
        print(ret)
                

        
        
requestable_dict = {
    'binary': 'Is your problem a binary classification one?', 
    'multiclass': 'Is your problem a multiclass problem of more than 2 classes?', 
    'nn': 'Do you plan to use a neural network?', 
    'ml': 'Do you plan to use machine learning algorithms?'
}


fact_recaps = {
    
    'binary': '- You need to classify data between 2 classes.', 
    'multiclass': '- You need to classify data between 2 classes.', 
    'nn': '- You want to use a neural network.', 
    'ml': '- You want to use basic machine learning algorithms.',
    'mlp-softmax': '- I advise you to use a multilayer perceptron with a softmax activation on the output layer.',
    'mlp-sigmoid': '- I advise you to use a multilayer perceptron with a sigmoid activation on the output layer.',
    'softmax-regression': '- I advise you to use a softmax regression algorithm.',
    'logistic-regression': '- I advise you to use a logistic regression alogrithm.'
}



NNexpert = Expert(req=requestable_dict, recaps=fact_recaps, verb=False)

NNexpert.addRule((Rule("classification => classifier")))
NNexpert.addRule((Rule("classifier & binary => binary-classification")))
NNexpert.addRule((Rule("classifier & multiclass => multi-classification")))

NNexpert.addRule((Rule("multi-classification & nn => mlp-softmax")))
NNexpert.addRule((Rule("binary-classification & nn => mlp-sigmoid")))

NNexpert.addRule((Rule("multi-classification & ml => softmax-regression")))
NNexpert.addRule((Rule("binary-classification & ml => logistic-regression")))


BF = [Fact("classification", val=Value.true)]
NNexpert.Proceed(BF)


'''
# Purpose 
NNexpert.addRule((Rule("create-data => generative-model")))
NNexpert.addRule((Rule("analyze-data => classic-model")))

# Problem type
NNexpert.addRule((Rule("labelled-data => supervised")))
NNexpert.addRule((Rule("raw-data => unsupervised")))

# Classification problems
NNexpert.addRule((Rule("classic-model & multiclass => classifier")))
NNexpert.addRule((Rule("classifier & supervised => softmax-regression")))
NNexpert.addRule((Rule("classifier & unsupervised => kmeans")))

# Prediction problems
NNexpert.addRule((Rule("classic-model & prediction => estimator")))
NNexpert.addRule((Rule("temporal-data & supervised & estimator => time-series")))
NNexpert.addRule((Rule("linear-data & estimator => linear-regression")))
NNexpert.addRule((Rule("partially-linear-data & estimator => ensemble-learning")))
NNexpert.addRule((Rule("non-linear-data & estimator => random-forest & neural-network")))
'''
'''
NNexpert.addRule((Rule("image => convolution")))

NNexpert.addRule((Rule("text => ...")))
NNexpert.addRule((Rule("unbalanced-data & data-fixed => metrics-study")))
NNexpert.addRule((Rule("unbalanced-data & data-not-fixed => re-sampling")))
'''
