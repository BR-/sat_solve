# test files
	# there are some test files at the bottom of
	# http://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html
	# https://toughsat.appspot.com

import random
import timeit

class Boolean:
	def __init__(self, variables, name, inverted=False):
		self.variables = variables
		self.name = name
		self.inverted = inverted

	def get(self):
		return self.inverted != self.variables[self.name]

	def toggle(self):
		self.variables[self.name] = not self.variables[self.name]

	def __str__(self):
		if self.inverted:
			return "!" + self.name
		else:
			return self.name

class CNFClause:
	def __init__(self, vars):
		self.vars = vars

	def evaluate(self):
		ret = False
		for var in self.vars:
			ret = ret or var.get()
		return ret

	def __str__(self):
		return "+".join(str(var) for var in self.vars)

class CNF: #AND of ORs
	def from_human(expr):
		variables = {}
		clauses = []
		for clause in expr.split("*"):
			cl = []
			for var in clause.strip("()").split("+"):
				if var[0] == "!":
					cl.append(Boolean(variables, var[1:], True))
					variables[var[1:]] = None
				else:
					cl.append(Boolean(variables, var))
					variables[var] = None
			clauses.append(CNFClause(cl))
		return CNF(variables, clauses)

	def from_dimacs(dimacs):
		variables = {}
		clauses = []
		cl = []
		for line in dimacs:
			if line[0] == 'c':
				continue
			elif line[0] == 'p':
				p, problem_type, vars, cls = line.split()
				if problem_type != "cnf":
					raise Exception("invalid file type")
				for v in range(int(vars)):
					variables[str(v+1)] = None
			else:
				for var in line.split():
					var = int(var)
					if var == 0:
						clauses.append(CNFClause(cl))
						cl = []
					elif var < 0:
						cl.append(Boolean(variables, str(-1 * var), True))
					else:
						cl.append(Boolean(variables, str(var)))
		return CNF(variables, clauses)
		

	def __init__(self, variables, clauses):
		self.variables = variables
		self.clauses = clauses

	def evaluate(self):
		ret = True
		for clause in self.clauses:
			ret = ret and clause.evaluate()
		return ret

	def satisfied(self, rly=True):
		ret = []
		for clause in self.clauses:
			if rly == clause.evaluate():
				ret.append(clause)
		return ret

	def random(self):
		for var in self.variables:
			self.variables[var] = not random.getrandbits(1)

	def walksat(self, random_flip=0.2, gsat=False):
		self.random()
		reset_counter = 0
		reset_best = 0
		while not self.evaluate():
			orig = self.satisfied()
			if len(orig) > reset_best:
				#print(len(orig))
				reset_counter = 0
				reset_best = len(orig)
			else:
				reset_counter += 1
				if reset_counter > 500:
					self.random()
					reset_counter = 0
					reset_best = 0
					continue
			clause = random.choice(self.satisfied(False))
			if random.random() > random_flip:
				best_var = []
				best_sat = 0
				for var in clause.vars:
					var.toggle()
					if gsat:
						sat = sum(1 for o in self.clauses if o.evaluate())
					else:
						sat = sum(1 for o in orig if o.evaluate())
					if sat > best_sat:
						best_sat = sat
						best_var = [var]
					elif sat == best_sat:
						best_var.append(var)
					var.toggle()
				random.choice(best_var).toggle()
			else:
				random.choice(clause.vars).toggle()
		return True

	def __str__(self):
		return "(" + ")*(".join(str(cl) for cl in self.clauses) + ")"

cnf = CNF.from_human("(A+B)*(!B+C+!D)*(D+!E)")
print(cnf)
print(timeit.timeit(cnf.walksat, number=5))
print(cnf.variables)





# generate a harder test
vars = {}
for v in range(100):
	vars[str(v)] = not random.getrandbits(1)
expr = []
for clause in range(1000):
	cl = []
	attempt = False
	for _ in range(2):
		v = random.choice(list(vars.keys()))
		inv = not random.getrandbits(1)
		cl.append(Boolean(vars, v, inv))
		attempt = attempt or (inv != vars[v])
	if attempt:
		expr.append(cl)
string = "*".join("+".join(str(v) for v in cl) for cl in expr)
cnf = CNF.from_human(string)
#print(cnf)
print(len(cnf.clauses), "clauses")
print(timeit.timeit(cnf.walksat, number=5))
print(cnf.variables)







with open("A:\\sat.cnf", "r") as fh:
	cnf = CNF.from_dimacs(fh)
print(len(cnf.clauses), "clauses")
print(timeit.timeit(cnf.walksat, number=5))
print(cnf.variables)